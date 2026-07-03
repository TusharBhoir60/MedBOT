"""Updated benchmark tests using ReferralDecision and seeded mock adapters."""
import pytest

from backend.evaluation.benchmark import (
    RuleBasedBaseline,
    LLMOnlyBaseline,
    RAGOnlyBaseline,
    CMARWorkflowBaseline,
)
from backend.evaluation.datasets import PatientCase, Demographics, ReferralDecision


def _dengue_case() -> PatientCase:
    return PatientCase(
        patient_id="T01",
        demographics=Demographics(age=28, gender="F"),
        symptoms=["high fever", "pain behind eyes", "rash"],
        risk_factors=["none"],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision=ReferralDecision.IMMEDIATE_CLINIC,
    )


def _cardiac_case() -> PatientCase:
    return PatientCase(
        patient_id="T02",
        demographics=Demographics(age=55, gender="M"),
        symptoms=["severe chest pain", "radiating", "sweating"],
        risk_factors=["smoking"],
        ground_truth_diagnosis="Emergency (Cardiac)",
        urgency_label="critical",
        expected_referral_decision=ReferralDecision.ER,
    )


# ─── Baseline A: Rule-based ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rule_based_dengue():
    adapter = RuleBasedBaseline()
    assert adapter.get_name() == "Baseline A: Rule-based"
    result = await adapter.evaluate_case(_dengue_case())
    assert result["predicted_diagnosis"] == "Dengue"
    assert result["referral_decision"] == ReferralDecision.IMMEDIATE_CLINIC
    assert result["confidence"] == 0.80
    assert result["retrieved_docs"] == []


@pytest.mark.asyncio
async def test_rule_based_cardiac():
    adapter = RuleBasedBaseline()
    result = await adapter.evaluate_case(_cardiac_case())
    assert result["predicted_diagnosis"] == "Emergency (Cardiac)"
    assert result["referral_decision"] == ReferralDecision.ER


# ─── Baseline B: LLM-only ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_llm_only_baseline():
    adapter = LLMOnlyBaseline(seed=42)
    assert adapter.get_name() == "Baseline B: LLM-only"
    result = await adapter.evaluate_case(_dengue_case())
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert isinstance(result["referral_decision"], ReferralDecision)
    assert 0.6 <= result["confidence"] <= 0.9


# ─── Baseline C: RAG-only ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_only_baseline():
    adapter = RAGOnlyBaseline(seed=42)
    assert adapter.get_name() == "Baseline C: RAG-only"
    result = await adapter.evaluate_case(_dengue_case())
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert isinstance(result["referral_decision"], ReferralDecision)
    assert len(result["retrieved_docs"]) == 2


# ─── Baseline D: CMAR (mock mode) ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_cmar_mock_baseline():
    adapter = CMARWorkflowBaseline(seed=42, use_mock=True)
    assert adapter.get_name() == "Baseline D: CMAR + RAG"
    result = await adapter.evaluate_case(_dengue_case())
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert isinstance(result["referral_decision"], ReferralDecision)
    assert len(result["retrieved_docs"]) == 3


@pytest.mark.asyncio
async def test_cmar_baseline_returns_query():
    adapter = CMARWorkflowBaseline(seed=42, use_mock=True)
    result = await adapter.evaluate_case(_dengue_case())
    assert "query" in result
    assert len(result["query"]) > 0


@pytest.mark.asyncio
async def test_cmar_output_has_required_keys():
    """Validate the result schema contract using the mock path."""
    adapter = CMARWorkflowBaseline(seed=42, use_mock=True)
    result = await adapter.evaluate_case(_dengue_case())
    for key in ["predicted_diagnosis", "confidence", "referral_decision",
                "retrieved_docs", "similarity_scores", "citations", "query"]:
        assert key in result, f"Missing key: {key}"
