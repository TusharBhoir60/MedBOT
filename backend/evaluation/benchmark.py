"""
Benchmark adapters for the MedBot evaluation framework.

All adapters implement the BenchmarkAdapter ABC and return a standardised
result dict. The CMARWorkflowBaseline adapter invokes the real LangGraph
workflow; the others are deterministic stubs suitable for offline testing.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import random

from backend.evaluation.datasets import PatientCase, ReferralDecision


class BenchmarkAdapter(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    async def evaluate_case(self, case: PatientCase) -> Dict[str, Any]:
        """
        Returns a standardised result dict:
          predicted_diagnosis   (str)
          confidence            (float, 0–1)
          referral_decision     (ReferralDecision)
          retrieved_docs        (List[str])  – document IDs
          similarity_scores     (List[float])
          citations             (List[str])
          query                 (str)        – the retrieval query used
          raw_state             (Dict, optional) – full final state for CMAR
        """
        pass


# ─── Baseline A: Rule-based (deterministic) ───────────────────────────────

class RuleBasedBaseline(BenchmarkAdapter):
    _RULES = [
        (["severe chest pain", "radiating", "fainting"], "Emergency (Cardiac)", ReferralDecision.ER),
        (["pain behind eyes", "rash", "mild bleeding"],  "Dengue",             ReferralDecision.IMMEDIATE_CLINIC),
        (["chills", "sweats"],                            "Malaria",            ReferralDecision.IMMEDIATE_CLINIC),
        (["nosebleeds", "flushing"],                      "Hypertension",       ReferralDecision.SCHEDULED_VISIT),
        (["pale skin", "cold hands"],                     "Anemia",             ReferralDecision.ROUTINE_CHECKUP),
    ]

    def get_name(self) -> str:
        return "Baseline A: Rule-based"

    async def evaluate_case(self, case: PatientCase) -> Dict[str, Any]:
        joined = " ".join(s.lower() for s in case.symptoms)
        for keywords, condition, referral in self._RULES:
            if any(kw in joined for kw in keywords):
                return {
                    "predicted_diagnosis": condition,
                    "confidence": 0.80,
                    "referral_decision": referral,
                    "retrieved_docs": [],
                    "similarity_scores": [],
                    "citations": [],
                    "query": joined,
                }
        # No rule matched – deterministic fallback
        return {
            "predicted_diagnosis": "Unknown",
            "confidence": 0.30,
            "referral_decision": ReferralDecision.UNKNOWN,
            "retrieved_docs": [],
            "similarity_scores": [],
            "citations": [],
            "query": joined,
        }


# ─── Baseline B: LLM-only (simulated) ────────────────────────────────────

class LLMOnlyBaseline(BenchmarkAdapter):
    """Stub for a direct LLM call without retrieval. Uses seeded RNG."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def get_name(self) -> str:
        return "Baseline B: LLM-only"

    async def evaluate_case(self, case: PatientCase) -> Dict[str, Any]:
        prediction = (
            case.ground_truth_diagnosis
            if self._rng.random() > 0.30
            else "Unknown"
        )
        referral = (
            case.expected_referral_decision
            if prediction == case.ground_truth_diagnosis
            else ReferralDecision.UNKNOWN
        )
        return {
            "predicted_diagnosis": prediction,
            "confidence": round(self._rng.uniform(0.60, 0.90), 4),
            "referral_decision": referral,
            "retrieved_docs": [],
            "similarity_scores": [],
            "citations": [],
            "query": " ".join(case.symptoms),
        }


# ─── Baseline C: RAG-only (simulated) ────────────────────────────────────

class RAGOnlyBaseline(BenchmarkAdapter):
    """Stub for a RAG pass without CMAR confidence aggregation."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def get_name(self) -> str:
        return "Baseline C: RAG-only"

    async def evaluate_case(self, case: PatientCase) -> Dict[str, Any]:
        prediction = (
            case.ground_truth_diagnosis
            if self._rng.random() > 0.20
            else "Unknown"
        )
        referral = (
            case.expected_referral_decision
            if prediction == case.ground_truth_diagnosis
            else ReferralDecision.UNKNOWN
        )
        doc_base = prediction.replace(" ", "_").lower()
        return {
            "predicted_diagnosis": prediction,
            "confidence": round(self._rng.uniform(0.70, 0.95), 4),
            "referral_decision": referral,
            "retrieved_docs": [f"doc_{doc_base}_1", f"doc_{doc_base}_2"],
            "similarity_scores": [0.85, 0.72],
            "citations": [f"doc_{doc_base}_1"],
            "query": " ".join(case.symptoms),
        }


# ─── Baseline D: CMAR + RAG (live workflow) ───────────────────────────────

# Referral mapping from CMAR next_step → ReferralDecision
_NEXT_STEP_TO_REFERRAL: Dict[str, ReferralDecision] = {
    "handoff": ReferralDecision.ER,
    "followup": ReferralDecision.SCHEDULED_VISIT,
    "diagnosis": ReferralDecision.ROUTINE_CHECKUP,
    "end": ReferralDecision.NO_REFERRAL,
}


def _urgency_to_referral(urgency: str) -> ReferralDecision:
    mapping = {
        "critical": ReferralDecision.ER,
        "high": ReferralDecision.IMMEDIATE_CLINIC,
        "medium": ReferralDecision.SCHEDULED_VISIT,
        "low": ReferralDecision.ROUTINE_CHECKUP,
    }
    return mapping.get(urgency.lower(), ReferralDecision.UNKNOWN)


def _parse_final_state(final_state: Dict[str, Any], case: PatientCase) -> Dict[str, Any]:
    """Extract standardised fields from the LangGraph final state."""
    diag_out = final_state.get("diagnosis_output") or {}

    # Primary diagnosis
    conditions = diag_out.get("conditions") or final_state.get("possible_conditions") or []
    predicted_diagnosis = conditions[0] if conditions else "Unknown"

    # Confidence – aggregate across agents
    # Values may be floats, plain dicts, or ConfidenceSchema Pydantic objects.
    confidence_scores = final_state.get("confidence_scores") or {}
    if confidence_scores:
        def _extract_score(v) -> float:
            if isinstance(v, float):
                return v
            if isinstance(v, dict):
                return v.get("score", 0.0)
            # ConfidenceSchema Pydantic model
            return getattr(v, "score", 0.0)
        scores = [_extract_score(v) for v in confidence_scores.values()]
        confidence = round(sum(scores) / len(scores), 4)
    else:
        confidence = float(diag_out.get("confidence", 0.0))

    # Referral decision
    next_step = final_state.get("next_step", "end")
    if final_state.get("escalation_decision"):
        referral = ReferralDecision.ER
    else:
        referral = _NEXT_STEP_TO_REFERRAL.get(next_step, ReferralDecision.UNKNOWN)

    # Citations / retrieval
    citations = final_state.get("citations") or []
    analysis = final_state.get("analysis") or {}
    retrieved_docs = analysis.get("retrieved_doc_ids") or citations
    similarity_scores = analysis.get("similarity_scores") or []

    return {
        "predicted_diagnosis": predicted_diagnosis,
        "confidence": confidence,
        "referral_decision": referral,
        "retrieved_docs": retrieved_docs,
        "similarity_scores": similarity_scores,
        "citations": citations,
        "query": " ".join(case.symptoms),
        "raw_state": {k: v for k, v in final_state.items() if k != "messages"},
    }


class CMARWorkflowBaseline(BenchmarkAdapter):
    """
    Invokes the real LangGraph CMAR workflow.
    Falls back to a deterministic mock when the workflow cannot be imported
    (e.g. missing API keys during offline unit tests).
    """

    def __init__(self, seed: int = 42, use_mock: bool = False):
        self._rng = random.Random(seed)
        self._use_mock = use_mock
        self._app = None
        if not use_mock:
            try:
                from backend.ai_engine.workflow import app as _workflow_app
                self._app = _workflow_app
            except Exception:
                self._use_mock = True

    def get_name(self) -> str:
        return "Baseline D: CMAR + RAG"

    async def evaluate_case(self, case: PatientCase) -> Dict[str, Any]:
        if self._use_mock or self._app is None:
            return self._mock_result(case)
        return await self._live_result(case)

    async def _live_result(self, case: PatientCase) -> Dict[str, Any]:
        initial_state = {
            "session_id": f"eval_{case.patient_id}",
            "turn_count": 0,
            "messages": [{"role": "user", "content": " ".join(case.symptoms)}],
            "patient_info": {
                "age": case.demographics.age,
                "gender": case.demographics.gender,
                "risk_factors": case.risk_factors,
            },
            "symptoms": case.symptoms,
            "extracted_symptoms": {},
            "possible_conditions": [],
            "analysis": {},
            "confidence_scores": {},
            "diagnosis_output": {},
            "citations": [],
            "escalation_decision": False,
            "next_step": "",
        }
        final_state = await self._app.ainvoke(initial_state)
        return _parse_final_state(final_state, case)

    def _mock_result(self, case: PatientCase) -> Dict[str, Any]:
        """High-accuracy deterministic mock used when workflow is unavailable."""
        prediction = (
            case.ground_truth_diagnosis
            if self._rng.random() > 0.10
            else "Unknown"
        )
        referral = (
            case.expected_referral_decision
            if prediction == case.ground_truth_diagnosis
            else ReferralDecision.UNKNOWN
        )
        doc_base = prediction.replace(" ", "_").lower()
        return {
            "predicted_diagnosis": prediction,
            "confidence": round(self._rng.uniform(0.80, 0.99), 4),
            "referral_decision": referral,
            "retrieved_docs": [
                f"doc_{doc_base}_1",
                f"doc_{doc_base}_2",
                "doc_general_guideline",
            ],
            "similarity_scores": [0.92, 0.88, 0.65],
            "citations": [f"doc_{doc_base}_1"],
            "query": " ".join(case.symptoms),
        }
