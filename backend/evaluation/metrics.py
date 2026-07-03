from typing import List, Dict, Any, Set, Optional
from collections import defaultdict
import math

from backend.evaluation.datasets import ReferralDecision


class MetricsCalculator:
    def __init__(self):
        pass

    # ─── Diagnostic Metrics ────────────────────────────────────────────────

    def compute_overall_metrics(self, ground_truths: List[str], predictions: List[str]) -> Dict[str, float]:
        if not ground_truths:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

        correct = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == pred)
        accuracy = correct / len(ground_truths)

        conditions = set(ground_truths)
        metrics_per_condition = self.compute_per_condition_metrics(ground_truths, predictions)

        if not conditions:
            return {"accuracy": accuracy, "precision": 0.0, "recall": 0.0, "f1": 0.0}

        avg_precision = sum(m["precision"] for m in metrics_per_condition.values()) / len(conditions)
        avg_recall = sum(m["recall"] for m in metrics_per_condition.values()) / len(conditions)

        avg_f1 = (
            2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
            if (avg_precision + avg_recall) > 0
            else 0.0
        )

        return {
            "accuracy": accuracy,
            "precision": avg_precision,
            "recall": avg_recall,
            "f1": avg_f1,
        }

    def compute_per_condition_metrics(
        self, ground_truths: List[str], predictions: List[str]
    ) -> Dict[str, Dict[str, float]]:
        conditions = set(ground_truths)
        metrics = {}
        for condition in conditions:
            tp = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == condition and pred == condition)
            fp = sum(1 for gt, pred in zip(ground_truths, predictions) if gt != condition and pred == condition)
            fn = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == condition and pred != condition)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            metrics[condition] = {"precision": precision, "recall": recall, "f1": f1}
        return metrics

    def compute_confusion_matrix(
        self, ground_truths: List[str], predictions: List[str]
    ) -> Dict[str, Dict[str, int]]:
        conditions = set(ground_truths).union(set(predictions))
        matrix = {actual: {pred: 0 for pred in conditions} for actual in conditions}
        for gt, pred in zip(ground_truths, predictions):
            matrix[gt][pred] += 1
        return matrix

    # ─── Referral Metrics ──────────────────────────────────────────────────

    def compute_referral_metrics(
        self,
        gt_referrals: List[ReferralDecision],
        pred_referrals: List[ReferralDecision],
        emergency_decisions: Optional[Set[ReferralDecision]] = None,
        high_urgency_labels: Optional[List[str]] = None,
        urgency_labels: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        Compute referral-level metrics treating any non-NO_REFERRAL/UNKNOWN as a positive
        referral prediction.

        - referral_accuracy   : overall correct referral decisions
        - referral_precision  : of predicted referrals, how many were truly needed
        - referral_recall     : of true referrals, how many were caught
        - false_referral_rate : FP / (FP + TN) — unnecessary referrals among non-referral cases
        - missed_emergency_rate: proportion of emergency cases with incorrect referral prediction
        """
        if emergency_decisions is None:
            emergency_decisions = {ReferralDecision.ER, ReferralDecision.IMMEDIATE_CLINIC}

        def is_referral(d: ReferralDecision) -> bool:
            return d not in {ReferralDecision.NO_REFERRAL, ReferralDecision.UNKNOWN}

        def is_emergency(d: ReferralDecision) -> bool:
            return d in emergency_decisions

        n = len(gt_referrals)
        if n == 0:
            return {
                "referral_accuracy": 0.0,
                "referral_precision": 0.0,
                "referral_recall": 0.0,
                "false_referral_rate": 0.0,
                "missed_emergency_rate": 0.0,
            }

        correct = sum(1 for g, p in zip(gt_referrals, pred_referrals) if g == p)
        referral_accuracy = correct / n

        tp = sum(1 for g, p in zip(gt_referrals, pred_referrals) if is_referral(g) and is_referral(p))
        fp = sum(1 for g, p in zip(gt_referrals, pred_referrals) if not is_referral(g) and is_referral(p))
        fn = sum(1 for g, p in zip(gt_referrals, pred_referrals) if is_referral(g) and not is_referral(p))
        tn = sum(1 for g, p in zip(gt_referrals, pred_referrals) if not is_referral(g) and not is_referral(p))

        referral_precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        referral_recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        false_referral_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        emergency_cases = [(g, p) for g, p in zip(gt_referrals, pred_referrals) if is_emergency(g)]
        missed_emergency_rate = (
            sum(1 for g, p in emergency_cases if not is_emergency(p)) / len(emergency_cases)
            if emergency_cases
            else 0.0
        )

        return {
            "referral_accuracy": referral_accuracy,
            "referral_precision": referral_precision,
            "referral_recall": referral_recall,
            "false_referral_rate": false_referral_rate,
            "missed_emergency_rate": missed_emergency_rate,
        }

    # ─── High-Confidence Error Rate ────────────────────────────────────────

    def compute_high_confidence_error_rate(
        self,
        ground_truths: List[str],
        predictions: List[str],
        confidences: List[float],
        threshold: float = 0.8,
    ) -> float:
        """
        Returns the proportion of cases where the model was wrong but expressed
        confidence >= threshold. High values indicate overconfident errors.
        """
        high_conf_errors = sum(
            1
            for gt, pred, conf in zip(ground_truths, predictions, confidences)
            if conf >= threshold and gt != pred
        )
        high_conf_total = sum(1 for conf in confidences if conf >= threshold)
        return high_conf_errors / high_conf_total if high_conf_total > 0 else 0.0

    # ─── Retrieval Metrics ─────────────────────────────────────────────────

    def compute_retrieval_metrics(
        self,
        relevant_docs: List[Set[str]],
        retrieved_docs_lists: List[List[str]],
        k: int = 5,
    ) -> Dict[str, float]:
        if not relevant_docs or not retrieved_docs_lists:
            return {"recall_at_k": 0.0, "precision_at_k": 0.0, "mrr": 0.0, "ndcg": 0.0}

        total_queries = len(relevant_docs)
        sum_recall = sum_precision = sum_mrr = sum_ndcg = 0.0

        for relevant, retrieved in zip(relevant_docs, retrieved_docs_lists):
            top_k = retrieved[:k]
            hits = len(set(top_k).intersection(relevant))
            sum_recall += hits / len(relevant) if relevant else 0.0
            sum_precision += hits / k if k > 0 else 0.0

            rr = 0.0
            for i, doc in enumerate(retrieved):
                if doc in relevant:
                    rr = 1.0 / (i + 1)
                    break
            sum_mrr += rr

            dcg = sum(1.0 / math.log2(i + 2) for i, doc in enumerate(top_k) if doc in relevant)
            idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant), k)))
            sum_ndcg += dcg / idcg if idcg > 0 else 0.0

        return {
            "recall_at_k": sum_recall / total_queries,
            "precision_at_k": sum_precision / total_queries,
            "mrr": sum_mrr / total_queries,
            "ndcg": sum_ndcg / total_queries,
        }
