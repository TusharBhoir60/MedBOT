"""
AuditTrailBuilder: assembles a complete AuditTrail from workflow state
and Sprint 5 versioning metadata.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from schemas.patient_response import AuditTrail


# Centralised version constants — bump these on each sprint/release
WORKFLOW_VERSION = "v1"
PROMPT_VERSION = "v1"
CARE_PLAN_VERSION = "v1"
TRANSLATION_VERSION = "v1"


class AuditTrailBuilder:
    """
    Builds an AuditTrail from CMAR workflow state and external metadata.
    Accepts both ConfidenceSchema Pydantic objects and plain dicts/floats.
    """

    def build(
        self,
        session_id: str,
        confidence_scores: Dict[str, Any],
        citations: List[str] = None,
        timestamps: Dict[str, str] = None,
        experiment_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        embedding_model: Optional[str] = None,
        retrieval_top_k: Optional[int] = None,
    ) -> AuditTrail:
        scores_snapshot = self._extract_scores(confidence_scores)
        ts = dict(timestamps or {})
        ts.setdefault("generated_at", datetime.now(timezone.utc).isoformat())

        return AuditTrail(
            session_id=session_id,
            workflow_version=WORKFLOW_VERSION,
            experiment_id=experiment_id,
            dataset_version=dataset_version,
            prompt_version=PROMPT_VERSION,
            care_plan_version=CARE_PLAN_VERSION,
            embedding_model=embedding_model,
            retrieval_top_k=retrieval_top_k,
            translation_version=TRANSLATION_VERSION,
            confidence_scores_snapshot=scores_snapshot,
            retrieved_evidence_ids=list(citations or []),
            timestamps=ts,
        )

    @staticmethod
    def _extract_scores(confidence_scores: Dict[str, Any]) -> Dict[str, float]:
        """Normalise ConfidenceSchema objects, plain dicts, or floats to {agent: score}."""
        snapshot: Dict[str, float] = {}
        for agent, v in confidence_scores.items():
            if isinstance(v, float):
                snapshot[agent] = v
            elif isinstance(v, dict):
                snapshot[agent] = float(v.get("score", 0.0))
            else:
                # ConfidenceSchema Pydantic model
                snapshot[agent] = float(getattr(v, "score", 0.0))
        return snapshot
