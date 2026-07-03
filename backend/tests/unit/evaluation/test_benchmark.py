import pytest
import asyncio
from backend.evaluation.benchmark import RuleBasedBaseline, LLMOnlyBaseline, RAGOnlyBaseline, CMARWorkflowBaseline
from backend.evaluation.datasets import PatientCase, Demographics

@pytest.mark.asyncio
async def test_rule_based_baseline():
    baseline = RuleBasedBaseline()
    assert baseline.get_name() == "Baseline A: Rule-based"
    
    case = PatientCase(
        patient_id="test1",
        demographics=Demographics(age=30, gender="M"),
        symptoms=["severe chest pain", "sweating"],
        risk_factors=[],
        ground_truth_diagnosis="Emergency (Cardiac)",
        urgency_label="critical",
        expected_referral_decision="er"
    )
    
    result = await baseline.evaluate_case(case)
    assert result["predicted_diagnosis"] == "Emergency (Cardiac)"
    assert result["confidence"] == 0.8
    assert result["retrieved_docs"] == []

@pytest.mark.asyncio
async def test_llm_only_baseline():
    baseline = LLMOnlyBaseline()
    case = PatientCase(
        patient_id="test1",
        demographics=Demographics(age=30, gender="M"),
        symptoms=["fever"],
        risk_factors=[],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision="immediate_clinic"
    )
    result = await baseline.evaluate_case(case)
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert 0.6 <= result["confidence"] <= 0.9

@pytest.mark.asyncio
async def test_rag_only_baseline():
    baseline = RAGOnlyBaseline()
    case = PatientCase(
        patient_id="test1",
        demographics=Demographics(age=30, gender="M"),
        symptoms=["fever"],
        risk_factors=[],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision="immediate_clinic"
    )
    result = await baseline.evaluate_case(case)
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert len(result["retrieved_docs"]) == 2

@pytest.mark.asyncio
async def test_cmar_workflow_baseline():
    baseline = CMARWorkflowBaseline()
    case = PatientCase(
        patient_id="test1",
        demographics=Demographics(age=30, gender="M"),
        symptoms=["fever"],
        risk_factors=[],
        ground_truth_diagnosis="Dengue",
        urgency_label="high",
        expected_referral_decision="immediate_clinic"
    )
    result = await baseline.evaluate_case(case)
    assert result["predicted_diagnosis"] in ["Dengue", "Unknown"]
    assert len(result["retrieved_docs"]) == 3
