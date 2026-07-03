import pytest
from ai_engine.explainability.patient_explainer import PatientExplainer
from ai_engine.state import ConfidenceSchema

def test_explainability_happy_path():
    diag_out = {
        "primary_diagnosis": "Dengue",
        "differential_diagnoses": ["Malaria", "Typhoid"],
        "urgency_level": "urgent",
        "reasoning": "High fever and rash suggest Dengue. No history of travel.",
        "citations": ["guidelines/dengue_2024.pdf"],
        "retrieval_confidence": 0.85,
        "diagnosis_confidence": 0.9,
    }
    scores = {
        "diagnosis": ConfidenceSchema(
            score=0.9,
            source="diagnosis",
            reasoning="Clear symptoms",
            requires_followup=False,
            requires_human=False
        )
    }
    
    explainer = PatientExplainer()
    explanation = explainer.explain(diag_out, scores)
    
    # Check reasoning
    assert "Dengue" in explanation.reasoning_summary
    assert "urgent" in explanation.reasoning_summary
    assert "Malaria, Typhoid" in explanation.reasoning_summary
    
    # Check evidence
    assert len(explanation.evidence_bullets) == 2
    assert "Dengue 2024" in explanation.formatted_citations[0]
    
    # Check confidence
    assert "very high" in explanation.confidence_explanation.lower()
    
def test_explainability_missing_evidence():
    diag_out = {
        "primary_diagnosis": "Unknown",
        "differential_diagnoses": [],
        "urgency_level": "routine",
        "reasoning": "No symptoms match.",
        "citations": [],
        "retrieval_confidence": 0.0,
        "diagnosis_confidence": 0.2,
    }
    
    explainer = PatientExplainer()
    explanation = explainer.explain(diag_out, {})
    
    assert "No specific guidelines were retrieved" in explanation.evidence_bullets[0]
    assert "No differential diagnoses" in explanation.differential_summary
    assert "very low" in explanation.confidence_explanation.lower()
