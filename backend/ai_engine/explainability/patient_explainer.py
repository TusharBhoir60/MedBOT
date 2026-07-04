"""PatientExplainer: orchestrates all sub-modules to produce ExplanationOutput."""
from typing import Any, Dict, List

from schemas.patient_response import ExplanationOutput
from ai_engine.explainability.reasoning_builder import ReasoningBuilder
from ai_engine.explainability.evidence_formatter import EvidenceFormatter
from ai_engine.explainability.confidence_explainer import ConfidenceExplainer


class PatientExplainer:
    """
    Top-level orchestrator for the explainability layer.
    Consumes a `diagnosis_output` dict (as produced by DiagnosisAgent)
    and returns a fully populated `ExplanationOutput`.
    """

    def __init__(self) -> None:
        self._reasoning = ReasoningBuilder()
        self._evidence = EvidenceFormatter()
        self._confidence = ConfidenceExplainer()

    def explain(
        self,
        diagnosis_output: Dict[str, Any],
        confidence_scores: Dict[str, Any] = None,
    ) -> ExplanationOutput:
        """
        Args:
            diagnosis_output: dict from DiagnosisAgent.invoke()
            confidence_scores: ConfidenceSchema objects or dicts keyed by agent name
        """
        if confidence_scores is None:
            confidence_scores = {}

        # Extract scalar scores
        diag_conf = float(diagnosis_output.get("diagnosis_confidence", 0.0))
        retr_conf = float(diagnosis_output.get("retrieval_confidence", 0.0))

        # Determine escalation flags from confidence_scores
        requires_followup = any(
            getattr(v, "requires_followup", False) or (isinstance(v, dict) and v.get("requires_followup", False))
            for v in confidence_scores.values()
        )
        requires_human = any(
            getattr(v, "requires_human", False) or (isinstance(v, dict) and v.get("requires_human", False))
            for v in confidence_scores.values()
        )

        reasoning_summary = self._reasoning.build(diagnosis_output)
        evidence_bullets = self._evidence.format_bullets(diagnosis_output)
        formatted_citations = self._evidence.format_citations(
            diagnosis_output.get("citations", [])
        )
        confidence_explanation = self._confidence.explain(
            diag_conf, retr_conf, requires_followup, requires_human
        )

        diffs = diagnosis_output.get("differential_diagnoses", [])
        differential_summary = (
            f"Differentials considered: {', '.join(diffs[:5])}." if diffs
            else "No differential diagnoses were recorded."
        )

        return ExplanationOutput(
            reasoning_summary=reasoning_summary,
            evidence_bullets=evidence_bullets,
            formatted_citations=formatted_citations,
            confidence_explanation=confidence_explanation,
            differential_summary=differential_summary,
        )
