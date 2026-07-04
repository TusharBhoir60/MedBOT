"""Unit tests for ExperimentManager."""
import json
import os
import tempfile
import pytest

from backend.evaluation.experiment_manager import ExperimentManager, _get_git_commit, _get_package_versions


def test_git_commit_is_string_or_none():
    result = _get_git_commit()
    assert result is None or isinstance(result, str)


def test_package_versions_returns_dict():
    versions = _get_package_versions()
    assert isinstance(versions, dict)
    assert "pydantic" in versions


def test_experiment_manager_build_metadata(tmp_path):
    manager = ExperimentManager(
        exp_dir=str(tmp_path),
        dataset_version="v1",
        model_config={"llm_model": "gpt-test", "temperature": 0.1},
        seed=99,
    )
    meta = manager.build_metadata()

    assert meta["dataset_version"] == "v1"
    assert meta["random_seed"] == 99
    assert meta["model_config"]["llm_model"] == "gpt-test"
    assert meta["model_config"]["temperature"] == 0.1
    assert "python_version" in meta["environment"]
    assert "packages" in meta["environment"]
    assert "git" in meta


def test_experiment_manager_log_retrieval(tmp_path):
    manager = ExperimentManager(exp_dir=str(tmp_path))
    manager.log_retrieval(
        adapter_name="TestAdapter",
        patient_id="P001",
        query="fever chills",
        ranked_docs=["doc_1", "doc_2"],
        similarity_scores=[0.9, 0.8],
        citations=["doc_1"],
    )

    assert "TestAdapter" in manager._retrieval_log
    entry = manager._retrieval_log["TestAdapter"][0]
    assert entry["patient_id"] == "P001"
    assert entry["query"] == "fever chills"
    assert entry["ranked_docs"] == ["doc_1", "doc_2"]
    assert entry["similarity_scores"] == [0.9, 0.8]
    assert entry["citations"] == ["doc_1"]


def test_experiment_manager_save_creates_files(tmp_path):
    manager = ExperimentManager(exp_dir=str(tmp_path), seed=7)
    manager.log_retrieval("A", "P000", "test query", ["d1"], [0.5], [])
    manager.save()

    assert os.path.exists(os.path.join(str(tmp_path), "metadata.json"))
    assert os.path.exists(os.path.join(str(tmp_path), "retrieval_diagnostics.json"))

    with open(os.path.join(str(tmp_path), "metadata.json")) as f:
        meta = json.load(f)
    assert meta["random_seed"] == 7

    with open(os.path.join(str(tmp_path), "retrieval_diagnostics.json")) as f:
        diag = json.load(f)
    assert "A" in diag


def test_experiment_manager_load_roundtrip(tmp_path):
    manager = ExperimentManager(
        exp_dir=str(tmp_path),
        dataset_version="v2",
        seed=55,
    )
    manager.save()

    loaded = ExperimentManager.load(str(tmp_path))
    assert loaded.dataset_version == "v2"
    assert loaded.seed == 55


def test_experiment_manager_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ExperimentManager.load(str(tmp_path))
