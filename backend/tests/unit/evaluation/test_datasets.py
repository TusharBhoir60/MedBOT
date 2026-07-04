"""Tests for datasets.py including ReferralDecision enum and versioned loading."""
import json
import os
import pytest

from backend.evaluation.datasets import (
    ReferralDecision,
    PatientCase,
    Demographics,
    load_dataset,
    _resolve_dataset_path,
)


def test_referral_decision_enum_values():
    assert ReferralDecision.ER.value == "er"
    assert ReferralDecision.IMMEDIATE_CLINIC.value == "immediate_clinic"
    assert ReferralDecision.SCHEDULED_VISIT.value == "scheduled_visit"
    assert ReferralDecision.ROUTINE_CHECKUP.value == "routine_checkup"
    assert ReferralDecision.NO_REFERRAL.value == "no_referral"
    assert ReferralDecision.UNKNOWN.value == "unknown"


def test_patient_case_enum_field():
    case = PatientCase(
        patient_id="T01",
        demographics=Demographics(age=30, gender="F"),
        symptoms=["fever"],
        risk_factors=[],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision=ReferralDecision.IMMEDIATE_CLINIC,
    )
    assert case.expected_referral_decision == ReferralDecision.IMMEDIATE_CLINIC


def test_load_json_dataset_via_version():
    """Load via manifest/version string (v1)."""
    cases = load_dataset("v1")
    assert len(cases) == 50
    assert isinstance(cases[0], PatientCase)
    assert isinstance(cases[0].expected_referral_decision, ReferralDecision)


def test_load_dataset_latest():
    """'latest' version alias resolves correctly."""
    cases = load_dataset("latest")
    assert len(cases) > 0


def test_load_csv_dataset():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    csv_path = os.path.join(base, "data", "eval", "v1", "mock_dataset.csv")
    if os.path.exists(csv_path):
        cases = load_dataset(csv_path)
        assert len(cases) == 50
        assert isinstance(cases[0].expected_referral_decision, ReferralDecision)


def test_load_dataset_invalid_extension():
    """A non-existent path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_dataset("v999")


def test_load_dataset_unsupported_extension(tmp_path):
    """An existing file with unsupported extension raises ValueError."""
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("dummy")
    with pytest.raises(ValueError):
        load_dataset(str(txt_file))
