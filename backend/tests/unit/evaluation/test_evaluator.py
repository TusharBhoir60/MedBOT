"""Updated evaluator end-to-end test with new schema."""
import json
import os
import pytest

from backend.evaluation.evaluator import Evaluator
from backend.evaluation.benchmark import (
    RuleBasedBaseline,
    LLMOnlyBaseline,
    RAGOnlyBaseline,
    CMARWorkflowBaseline,
)


@pytest.mark.asyncio
async def test_evaluator_end_to_end():
    adapters = [
        RuleBasedBaseline(),
        LLMOnlyBaseline(seed=42),
        RAGOnlyBaseline(seed=42),
        CMARWorkflowBaseline(seed=42, use_mock=True),
    ]
    ev = Evaluator(data_path="v1", seed=42, dataset_version="v1")
    exp_dir = await ev.run_evaluation(adapters=adapters)

    # Check all required artifact files exist
    for filename in [
        "metrics.json",
        "predictions.json",
        "calibration.json",
        "benchmark_summary.json",
        "confusion_matrix.json",
        "metadata.json",
        "retrieval_diagnostics.json",
        "report.md",
    ]:
        assert os.path.exists(os.path.join(exp_dir, filename)), \
            f"Missing artifact: {filename}"

    # Validate benchmark_summary structure
    with open(os.path.join(exp_dir, "benchmark_summary.json")) as f:
        summary = json.load(f)

    assert len(summary) == 4  # 4 adapters
    for name, s in summary.items():
        assert "accuracy" in s
        assert "f1" in s
        assert "referral_accuracy" in s
        assert "missed_emergency_rate" in s
        assert "high_confidence_error_rate" in s


@pytest.mark.asyncio
async def test_evaluator_metadata_fields():
    adapters = [
        RuleBasedBaseline(),
        LLMOnlyBaseline(seed=42),
        RAGOnlyBaseline(seed=42),
        CMARWorkflowBaseline(seed=42, use_mock=True),
    ]
    ev = Evaluator(
        data_path="v1",
        seed=42,
        dataset_version="v1",
        model_config={"llm_model": "test-model", "temperature": 0.0},
    )
    exp_dir = await ev.run_evaluation(adapters=adapters)

    with open(os.path.join(exp_dir, "metadata.json")) as f:
        meta = json.load(f)

    assert meta["dataset_version"] == "v1"
    assert meta["random_seed"] == 42
    assert meta["model_config"]["llm_model"] == "test-model"
    assert "git" in meta
    assert "environment" in meta
