import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, text, cast, Float, String, desc
from models.chat import ChatSession
from models.review import ReviewTask, ReviewStatus, ReviewComment

logger = logging.getLogger(__name__)

class MetricsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_date_filter(self, stmt, model_column, start_date: Optional[datetime], end_date: Optional[datetime]):
        if start_date:
            stmt = stmt.where(model_column >= start_date)
        if end_date:
            stmt = stmt.where(model_column < end_date)
        return stmt

    def _extract_json_float(self, column, *keys):
        """Helper to extract a float from a JSON column across dialects."""
        expr = column
        for key in keys:
            expr = expr[key]
        return cast(expr, Float)

    def _extract_json_string(self, column, *keys):
        """Helper to extract a string from a JSON column across dialects."""
        expr = column
        for key in keys:
            expr = expr[key]
        return cast(expr, String)

    async def get_overview_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        # Total Conversations
        stmt = select(func.count(ChatSession.id))
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        total_conversations = (await self.session.execute(stmt)).scalar() or 0

        # Review Tasks Counts
        stmt = select(ReviewTask.status, func.count(ReviewTask.id)).group_by(ReviewTask.status)
        stmt = self._apply_date_filter(stmt, ReviewTask.created_at, start_date, end_date)
        status_counts = dict((await self.session.execute(stmt)).all())

        total_review_tasks = sum(status_counts.values())

        # Average Confidence
        stmt = select(func.avg(self._extract_json_float(ChatSession.state, 'confidence_scores', 'combined', 'score')))
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        avg_conf = (await self.session.execute(stmt)).scalar()

        # Average Review Time
        # Only for resolved statuses: APPROVED, REJECTED, OVERRIDDEN, CLOSED
        resolved_statuses = [ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.OVERRIDDEN, ReviewStatus.CLOSED]
        
        # SQLite doesn't have extract(epoch), so we might need a workaround or fetch and calc. 
        # But wait, we can just do avg of (updated_at - created_at). In PostgreSQL it returns an interval, in SQLite a float?
        # To be dialect-safe, let's fetch the timestamps and average in python.
        stmt = select(ReviewTask.created_at, ReviewTask.updated_at).where(ReviewTask.status.in_(resolved_statuses))
        stmt = self._apply_date_filter(stmt, ReviewTask.updated_at, start_date, end_date) # Filter by resolution time
        resolved_tasks = (await self.session.execute(stmt)).all()
        
        avg_review_time = None
        if resolved_tasks:
            total_seconds = sum((t.updated_at - t.created_at).total_seconds() for t in resolved_tasks if t.updated_at and t.created_at)
            avg_review_time = total_seconds / len(resolved_tasks)

        # Average Messages Per Conversation
        # Dialect-safe: fetch and count in Python, or use DB-specific json_array_length.
        # Given we want to avoid loading full JSONB state, we can use a raw SQL snippet or fallback.
        # But SQLite doesn't natively support len(json_array) in SQLAlchemy without func.json_array_length.
        # Let's fetch the lists since they are relatively small, or use a hybrid approach.
        stmt = select(ChatSession.state['messages'])
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        messages_data = (await self.session.execute(stmt)).scalars().all()
        
        avg_messages = None
        if messages_data:
            total_msgs = sum(len(msgs) if isinstance(msgs, list) else 0 for msgs in messages_data)
            avg_messages = total_msgs / len(messages_data)

        # Escalation Rate
        # Distinct conversations with at least one review task / total conversations
        stmt = select(func.count(func.distinct(ReviewTask.session_id)))
        # Here we filter the review tasks by the same date range (or we can just use the overall sessions)
        stmt = self._apply_date_filter(stmt, ReviewTask.created_at, start_date, end_date)
        escalated_sessions = (await self.session.execute(stmt)).scalar() or 0
        
        escalation_rate = (escalated_sessions / total_conversations) if total_conversations > 0 else None

        return {
            "total_conversations": total_conversations,
            "total_review_tasks": total_review_tasks,
            "pending_reviews": status_counts.get(ReviewStatus.NEW, 0),
            "assigned_reviews": status_counts.get(ReviewStatus.ASSIGNED, 0),
            "under_review": status_counts.get(ReviewStatus.UNDER_REVIEW, 0),
            "approved_reviews": status_counts.get(ReviewStatus.APPROVED, 0),
            "rejected_reviews": status_counts.get(ReviewStatus.REJECTED, 0),
            "overridden_reviews": status_counts.get(ReviewStatus.OVERRIDDEN, 0),
            "closed_reviews": status_counts.get(ReviewStatus.CLOSED, 0),
            "average_confidence": avg_conf,
            "average_review_time_seconds": avg_review_time,
            "escalation_rate": escalation_rate,
            "average_messages_per_conversation": avg_messages,
        }

    async def get_confidence_metrics(self, low_threshold: float, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        conf_expr = self._extract_json_float(ChatSession.state, 'confidence_scores', 'combined', 'score')
        
        # Valid confidence filter: 0.0 <= score <= 1.0
        stmt = select(conf_expr).where(conf_expr >= 0.0).where(conf_expr <= 1.0)
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        
        scores = (await self.session.execute(stmt)).scalars().all()
        scores = [s for s in scores if s is not None]
        
        avg_conf = sum(scores) / len(scores) if scores else None
        min_conf = min(scores) if scores else None
        max_conf = max(scores) if scores else None
        sample_size = len(scores)
        
        buckets = [
            {"minimum": 0.0, "maximum": 0.2, "count": 0},
            {"minimum": 0.2, "maximum": 0.4, "count": 0},
            {"minimum": 0.4, "maximum": 0.6, "count": 0},
            {"minimum": 0.6, "maximum": 0.8, "count": 0},
            {"minimum": 0.8, "maximum": 1.0, "count": 0},
        ]
        
        low_confidence_cases = 0
        for s in scores:
            if s < low_threshold:
                low_confidence_cases += 1
                
            if s < 0.2:
                buckets[0]["count"] += 1
            elif s < 0.4:
                buckets[1]["count"] += 1
            elif s < 0.6:
                buckets[2]["count"] += 1
            elif s < 0.8:
                buckets[3]["count"] += 1
            else:
                buckets[4]["count"] += 1

        # Agent averages
        # Dialect-safe extraction: load only the confidence_scores dict
        stmt = select(ChatSession.state['confidence_scores'])
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        all_conf_scores = (await self.session.execute(stmt)).scalars().all()
        
        agent_totals: Dict[str, float] = {}
        agent_counts: Dict[str, int] = {}
        for scores_dict in all_conf_scores:
            if not isinstance(scores_dict, dict):
                continue
            for agent, data in scores_dict.items():
                if agent == 'combined':
                    continue
                if isinstance(data, dict) and 'score' in data:
                    score = data['score']
                    if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
                        agent_totals[agent] = agent_totals.get(agent, 0.0) + float(score)
                        agent_counts[agent] = agent_counts.get(agent, 0) + 1
                        
        agent_averages = [
            {"agent": a, "average": agent_totals[a] / agent_counts[a], "sample_size": agent_counts[a]}
            for a in agent_counts
        ]

        # Condition averages
        stmt = select(
            self._extract_json_string(ChatSession.state, 'diagnosis_output', 'primary_diagnosis'),
            conf_expr
        ).where(conf_expr >= 0.0).where(conf_expr <= 1.0)
        stmt = self._apply_date_filter(stmt, ChatSession.created_at, start_date, end_date)
        
        condition_data = (await self.session.execute(stmt)).all()
        cond_totals: Dict[str, float] = {}
        cond_counts: Dict[str, int] = {}
        
        for cond, score in condition_data:
            if cond and score is not None:
                cond = cond.strip()
                if cond:
                    cond_totals[cond] = cond_totals.get(cond, 0.0) + float(score)
                    cond_counts[cond] = cond_counts.get(cond, 0) + 1
                    
        condition_averages = [
            {"condition": c, "average": cond_totals[c] / cond_counts[c], "sample_size": cond_counts[c]}
            for c in cond_counts
        ]
        
        # Sort for consistency
        agent_averages.sort(key=lambda x: x['agent'])
        condition_averages.sort(key=lambda x: x['sample_size'], reverse=True)

        return {
            "average_confidence": avg_conf,
            "minimum_confidence": min_conf,
            "maximum_confidence": max_conf,
            "sample_size": sample_size,
            "distribution": buckets,
            "agent_averages": agent_averages,
            "condition_averages": condition_averages[:20], # top 20
            "low_confidence_cases": low_confidence_cases,
            "low_confidence_threshold": low_threshold,
        }

    async def get_review_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        stmt = select(ReviewTask.status, func.count(ReviewTask.id)).group_by(ReviewTask.status)
        stmt = self._apply_date_filter(stmt, ReviewTask.created_at, start_date, end_date)
        status_counts = dict((await self.session.execute(stmt)).all())
        
        total = sum(status_counts.values())
        
        # Resolved tasks for rates
        resolved_statuses = [ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.OVERRIDDEN, ReviewStatus.CLOSED]
        
        # To calculate accurate rates based on RESOLVED tasks within the date range,
        # we should filter by updated_at for resolution.
        stmt_resolved = select(ReviewTask.status, func.count(ReviewTask.id)).where(ReviewTask.status.in_(resolved_statuses))
        stmt_resolved = self._apply_date_filter(stmt_resolved, ReviewTask.updated_at, start_date, end_date)
        stmt_resolved = stmt_resolved.group_by(ReviewTask.status)
        resolved_counts = dict((await self.session.execute(stmt_resolved)).all())
        
        resolved_total = sum(resolved_counts.values())
        
        # Resolution Time & Throughput
        stmt_times = select(ReviewTask.created_at, ReviewTask.updated_at).where(ReviewTask.status.in_(resolved_statuses))
        stmt_times = self._apply_date_filter(stmt_times, ReviewTask.updated_at, start_date, end_date)
        resolved_tasks = (await self.session.execute(stmt_times)).all()
        
        avg_res_time = None
        throughput_dict = {}
        if resolved_tasks:
            total_seconds = 0
            for t in resolved_tasks:
                if t.updated_at and t.created_at:
                    total_seconds += max(0, (t.updated_at - t.created_at).total_seconds())
                
                # Throughput date grouping (UTC Date string)
                if t.updated_at:
                    date_str = t.updated_at.strftime('%Y-%m-%d')
                    throughput_dict[date_str] = throughput_dict.get(date_str, 0) + 1
                    
            avg_res_time = total_seconds / len(resolved_tasks)
            
        throughput = [{"date": k, "count": v} for k, v in sorted(throughput_dict.items())]

        return {
            "total": total,
            "new": status_counts.get(ReviewStatus.NEW, 0),
            "assigned": status_counts.get(ReviewStatus.ASSIGNED, 0),
            "under_review": status_counts.get(ReviewStatus.UNDER_REVIEW, 0),
            "approved": status_counts.get(ReviewStatus.APPROVED, 0),
            "rejected": status_counts.get(ReviewStatus.REJECTED, 0),
            "overridden": status_counts.get(ReviewStatus.OVERRIDDEN, 0),
            "closed": status_counts.get(ReviewStatus.CLOSED, 0),
            "approval_rate": (resolved_counts.get(ReviewStatus.APPROVED, 0) / resolved_total) if resolved_total > 0 else None,
            "rejection_rate": (resolved_counts.get(ReviewStatus.REJECTED, 0) / resolved_total) if resolved_total > 0 else None,
            "override_rate": (resolved_counts.get(ReviewStatus.OVERRIDDEN, 0) / resolved_total) if resolved_total > 0 else None,
            "average_resolution_time_seconds": avg_res_time,
            "throughput": throughput,
        }

    async def get_clinical_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        # Symptoms, Conditions, Severity from ReviewTask
        # Since jsonb_array_elements_text is PostgreSQL only, we fetch the data and aggregate in Python
        stmt = select(ReviewTask.symptoms, ReviewTask.diagnosis_output, ReviewTask.status)
        stmt = self._apply_date_filter(stmt, ReviewTask.created_at, start_date, end_date)
        tasks = (await self.session.execute(stmt)).all()
        
        symptoms_count: Dict[str, int] = {}
        conditions_count: Dict[str, int] = {}
        severity_count: Dict[str, int] = {}
        status_count: Dict[str, int] = {}
        
        sample_size = len(tasks)
        
        for symptoms_list, diagnosis_output, status in tasks:
            # Symptoms
            if isinstance(symptoms_list, list):
                for sym in symptoms_list:
                    if sym and isinstance(sym, str):
                        clean_sym = sym.strip().lower()
                        # Preserve original readable label case by using Title Case or just lower for grouping
                        # The requirement says "Preserve a readable display label."
                        # We'll group by lower, but store the first seen label.
                        display_label = sym.strip().capitalize()
                        if clean_sym:
                            if clean_sym not in symptoms_count:
                                symptoms_count[clean_sym] = {"label": display_label, "count": 0}
                            symptoms_count[clean_sym]["count"] += 1
                            
            # Conditions & Severity
            if isinstance(diagnosis_output, dict):
                cond = diagnosis_output.get("primary_diagnosis") or diagnosis_output.get("diagnosis")
                if cond and isinstance(cond, str):
                    clean_cond = cond.strip().lower()
                    if clean_cond:
                        if clean_cond not in conditions_count:
                            conditions_count[clean_cond] = {"label": cond.strip(), "count": 0}
                        conditions_count[clean_cond]["count"] += 1
                        
                sev = diagnosis_output.get("urgency_level")
                if sev and isinstance(sev, str):
                    clean_sev = sev.strip().lower()
                    if clean_sev:
                        if clean_sev not in severity_count:
                            severity_count[clean_sev] = {"label": sev.strip().capitalize(), "count": 0}
                        severity_count[clean_sev]["count"] += 1
            
            # Escalation (Status distribution)
            if status:
                s_name = status.value if hasattr(status, 'value') else str(status)
                status_count[s_name] = status_count.get(s_name, 0) + 1

        top_symptoms = [{"name": v["label"], "count": v["count"]} for v in sorted(symptoms_count.values(), key=lambda x: x["count"], reverse=True)]
        top_conditions = [{"name": v["label"], "count": v["count"]} for v in sorted(conditions_count.values(), key=lambda x: x["count"], reverse=True)]
        severity_dist = [{"name": v["label"], "count": v["count"]} for v in sorted(severity_count.values(), key=lambda x: x["count"], reverse=True)]
        escalation_dist = [{"name": k, "count": v} for k, v in sorted(status_count.items(), key=lambda x: x[1], reverse=True)]

        return {
            "top_symptoms": top_symptoms[:50], # Limit to top 50
            "top_conditions": top_conditions[:50],
            "severity_distribution": severity_dist,
            "escalation_distribution": escalation_dist,
            "sample_size": sample_size
        }

    async def get_activity_feed(self, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Activity Feed combining recent conversations and review tasks.
        Uses timestamp + ID string comparison for stable cursoring.
        """
        # Fetching recently created entities
        # A true cursor needs an exact ordering constraint. We use created_at (desc).
        # We query ChatSessions and ReviewTasks
        
        session_stmt = select(ChatSession.id, ChatSession.created_at).order_by(desc(ChatSession.created_at)).limit(limit + 1)
        task_stmt = select(ReviewTask.id, ReviewTask.created_at, ReviewTask.status).order_by(desc(ReviewTask.created_at)).limit(limit + 1)
        
        # If cursor provided, it's expected as "timestamp_iso|id"
        if cursor:
            try:
                cursor_time_str, cursor_id = cursor.split('|', 1)
                cursor_time = datetime.fromisoformat(cursor_time_str)
                # Where (created_at < cursor_time) OR (created_at == cursor_time AND id < cursor_id)
                session_stmt = session_stmt.where(ChatSession.created_at <= cursor_time)
                task_stmt = task_stmt.where(ReviewTask.created_at <= cursor_time)
            except ValueError:
                pass # Invalid cursor format, ignore
                
        sessions = (await self.session.execute(session_stmt)).all()
        tasks = (await self.session.execute(task_stmt)).all()
        
        items = []
        for s in sessions:
            items.append({
                "id": str(s.id),
                "type": "conversation_created",
                "description": "Conversation created",
                "timestamp": s.created_at.isoformat()
            })
            
        for t in tasks:
            status = t.status.value if hasattr(t.status, 'value') else str(t.status)
            desc_text = f"Review {status.lower()}"
            if status == "NEW":
                desc_text = "Review task created"
            elif status == "ASSIGNED":
                desc_text = "Review assigned"
            elif status == "APPROVED":
                desc_text = "Review approved"
            elif status == "REJECTED":
                desc_text = "Review rejected"
            elif status == "OVERRIDDEN":
                desc_text = "Review overridden"
                
            items.append({
                "id": str(t.id),
                "type": f"review_{status.lower()}",
                "description": desc_text,
                "timestamp": t.created_at.isoformat()
            })
            
        # Sort combined items desc
        items.sort(key=lambda x: (x["timestamp"], x["id"]), reverse=True)
        
        # Filter strictly by cursor if provided
        if cursor:
            items = [i for i in items if f"{i['timestamp']}|{i['id']}" < cursor]
            
        has_next = len(items) > limit
        items = items[:limit]
        
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            next_cursor = f"{last_item['timestamp']}|{last_item['id']}"
            
        return {
            "items": items,
            "next_cursor": next_cursor
        }
