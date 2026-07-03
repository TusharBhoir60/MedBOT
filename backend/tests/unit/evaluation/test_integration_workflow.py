"""
Integration test: verifies that predictions produced by CMARWorkflowBaseline
(mocked here to avoid LLM calls) are exactly preserved in the evaluation
framework's output artifacts.
"""
import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.evaluation.datasets import PatientCase, Demographics, ReferralDecision
from backend.evaluation.benchmark import CMARWorkflowBaseline, _parse_final_state
from backend.evaluation.evaluator import Evaluator


# ─── Helpers ──────────────────────────────────────────────────────────────

def _make_case(patient_id: str = "P_INT_001") -> PatientCase:
    return PatientCase(
        patient_id=patient_id,
        demographics=Demographics(age=35, gender="M"),
        symptoms=["high fever", "joint pain", "rash"],
        risk_factors=["none"],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision=ReferralDecision.IMMEDIATE_CLINIC,
    )


def _mock_final_state(condition: str = "Dengue") -> dict:
    return {
        "session_id": "eval_P_INT_001",
        "turn_count": 3,
        "messages": [],
        "patient_info": {},
        "symptoms": ["high fever", "joint pain", "rash"],
        "extracted_symptoms": {},
        "possible_conditions": [condition],
        "analysis": {
            "retrieved_doc_ids": [f"doc_{condition.lower()}_1"],
            "similarity_scores": [0.91],
        },
        "confidence_scores": {"symptom_agent": {"score": 0.87, "source": "symptom_agent",
                                                 "reasoning": "", "uncertainty_factors": [],
                                                 "requires_followup": False, "requires_human": False}},
        "diagnosis_output": {"conditions": [condition], "confidence": 0.87},
        "citations": [f"doc_{condition.lower()}_1"],
        "escalation_decision": False,
        "next_step": "diagnosis",
    }


# ─── Tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_final_state_extracts_fields():
    case = _make_case()
    state = _mock_final_state("Dengue")
    result = _parse_final_state(state, case)

    assert result["predicted_diagnosis"] == "Dengue"
    assert result["confidence"] == pytest.approx(0.87, rel=1e-3)
    assert result["referral_decision"] == ReferralDecision.ROUTINE_CHECKUP  # next_step=diagnosis
    assert "doc_dengue_1" in result["retrieved_docs"]
    assert "doc_dengue_1" in result["citations"]


@pytest.mark.asyncio
async def test_cmar_baseline_live_result_matches_state():
    """Live path: ainvoke is mocked; verifies the parsed output matches the state."""
    mock_app = MagicMock()
    mock_app.ainvoke = AsyncMock(return_value=_mock_final_state("Dengue"))

    adapter = CMARWorkflowBaseline(seed=42, use_mock=False)
    adapter._app = mock_app
    adapter._use_mock = False

    case = _make_case()
    result = await adapter.evaluate_case(case)

    assert result["predicted_diagnosis"] == "Dengue"
    assert result["confidence"] == pytest.approx(0.87, rel=1e-3)
    mock_app.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_evaluator_predictions_match_adapter_output(tmp_path, monkeypatch):
    """
    End-to-end: run Evaluator with a mocked CMARWorkflowBaseline and verify
    that predictions.json contains exactly the same diagnosis the adapter returned.
    """
    import backend.evaluation.evaluator as evaluator_mod

    # Monkeypatch load_dataset to return a single deterministic case
    case = _make_case()
    monkeypatch.setattr(evaluator_mod, "load_dataset", lambda _path: [case])

    # Patch Evaluator._create_experiment_dir to use tmp_path
    monkeypatch.setattr(
        evaluator_mod.Evaluator,
        "_create_experiment_dir",
        lambda self: str(tmp_path),
    )

    adapter = CMARWorkflowBaseline(seed=42, use_mock=False)
    mock_app = MagicMock()
    mock_app.ainvoke = AsyncMock(return_value=_mock_final_state("Dengue"))
    adapter._app = mock_app
    adapter._use_mock = False

    ev = Evaluator(data_path="v1", seed=42)
    await ev.run_evaluation(adapters=[adapter])

    preds_path = os.path.join(str(tmp_path), "predictions.json")
    assert os.path.exists(preds_path)

    with open(preds_path, "r") as f:
        preds = json.load(f)

    adapter_preds = preds["Baseline D: CMAR + RAG"]
    assert len(adapter_preds) == 1
    assert adapter_preds[0]["predicted_diagnosis"] == "Dengue"
    assert adapter_preds[0]["patient_id"] == "P_INT_001"


@pytest.mark.asyncio
async def test_metadata_json_created(tmp_path, monkeypatch):
    """Verify metadata.json is created and contains expected fields."""
    import backend.evaluation.evaluator as evaluator_mod

    case = _make_case()
    monkeypatch.setattr(evaluator_mod, "load_dataset", lambda _path: [case])
    monkeypatch.setattr(
        evaluator_mod.Evaluator,
        "_create_experiment_dir",
        lambda self: str(tmp_path),
    )

    from backend.evaluation.benchmark import RuleBasedBaseline
    ev = Evaluator(data_path="v1", seed=42, dataset_version="v1",
                   model_config={"llm_model": "test-llm"})
    await ev.run_evaluation(adapters=[RuleBasedBaseline()])

    meta_path = os.path.join(str(tmp_path), "metadata.json")
    assert os.path.exists(meta_path)

    with open(meta_path, "r") as f:
        meta = json.load(f)

    assert meta["dataset_version"] == "v1"
    assert meta["model_config"]["llm_model"] == "test-llm"
    assert "environment" in meta
    assert "git" in meta
