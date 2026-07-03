"""Converts numeric confidence scores into plain-English explanations."""
from typing import Any, Dict


class ConfidenceExplainer:
    """Translates floating-point confidence into human-readable narrative."""

    # Confidence band thresholds and their labels
    _BANDS = [
        (0.85, "very high",   "The system is highly confident in this assessment."),
        (0.70, "high",        "The system has strong confidence in this assessment."),
        (0.50, "moderate",    "The system has moderate confidence; a clinical review is advisable."),
        (0.30, "low",         "The system has limited confidence. A healthcare provider should be consulted."),
        (0.00, "very low",    "Confidence is very low. Please consult a doctor immediately."),
    ]

    def explain(
        self,
        diagnosis_confidence: float,
        retrieval_confidence: float = 0.0,
        requires_followup: bool = False,
        requires_human: bool = False,
    ) -> str:
        """
        Returns a plain-English narrative describing confidence levels
        and any follow-up or escalation recommendations.
        """
        label, narrative = self._band(diagnosis_confidence)
        retrieval_label, _ = self._band(retrieval_confidence)

        parts = [
            f"Diagnosis confidence is {label} ({int(diagnosis_confidence * 100)}%). {narrative}",
            f"Supporting evidence quality is {retrieval_label} ({int(retrieval_confidence * 100)}%).",
        ]

        if requires_human:
            parts.append("⚠ Human clinical review is required before acting on this output.")
        elif requires_followup:
            parts.append("A follow-up consultation is recommended to confirm this diagnosis.")

        return " ".join(parts)

    def _band(self, score: float):
        for threshold, label, text in self._BANDS:
            if score >= threshold:
                return label, text
        return "very low", self._BANDS[-1][2]
