import pytest
from typing import Any, Dict

from ai_engine.state import SharedState, ConfidenceSchema
from ai_engine.orchestrator.patient_response_builder import build_patient_response
from ai_engine.safety.response_validator import SafetyViolation


def _mock_state(
    primary_diagnosis: str = "Dengue",
    urgency_level: str = "urgent",
    next_step: str = "end",
    language: str = "en-IN"
) -> SharedState:
    return {
        "session_id": "test-session",
        "turn_count": 1,
        "messages": [],
        "patient_info": {"language": language, "age": 30},
        "symptoms": ["fever"],
        "extracted_symptoms": {},
        "possible_conditions": [primary_diagnosis],
        "analysis": {},
        "confidence_scores": {
            "diagnosis": ConfidenceSchema(
                score=0.85,
                source="diagnosis",
                reasoning="Reasoning",
                requires_followup=False,
                requires_human=False
            )
        },
        "diagnosis_output": {
            "primary_diagnosis": primary_diagnosis,
            "differential_diagnoses": ["Malaria"],
            "urgency_level": urgency_level,
            "reasoning": "High fever.",
            "citations": [],
            "retrieval_confidence": 0.8,
            "diagnosis_confidence": 0.85,
        },
        "citations": [],
        "escalation_decision": False,
        "next_step": next_step,
    }


@pytest.mark.asyncio
async def test_workflow_integration_happy_path():
    """Verify the orchestrator successfully builds a full PatientResponse."""
    state = _mock_state()
    updates = await build_patient_response(state)
    
    assert "patient_response" in updates
    resp = updates["patient_response"]
    
    # Assert fields are present and valid
    assert resp["diagnosis"] == "Dengue"
    assert "explanation" in resp
    assert "care_plan" in resp
    assert "audit_trail" in resp
    assert resp["language"] == "en-IN"


@pytest.mark.asyncio
async def test_workflow_integration_localization_hindi():
    """Verify the orchestrator localizes the response."""
    state = _mock_state(language="hi-IN")
    updates = await build_patient_response(state)
    
    resp = updates["patient_response"]
    assert resp["language"] == "hi-IN"
    assert resp["urgency_level"] == "तत्काल"
    assert "डेंगू" in resp["diagnosis"]


@pytest.mark.asyncio
async def test_workflow_integration_localization_fallback():
    """Verify unknown locales fallback gracefully."""
    state = _mock_state(language="fr-FR")
    updates = await build_patient_response(state)
    
    resp = updates["patient_response"]
    assert resp["language"] == "fr-FR"
    assert resp["urgency_level"] == "urgent"


@pytest.mark.asyncio
async def test_workflow_integration_safety_violation():
    """Verify the safety validator raises an exception if invariants are broken."""
    # We will trigger the empty session ID violation which is checked by ResponseValidator
    state = _mock_state()
    state["session_id"] = "   "
    
    with pytest.raises(SafetyViolation) as exc_info:
        await build_patient_response(state)
        
    assert "session_id" in str(exc_info.value)


@pytest.mark.asyncio
async def test_workflow_integration_emergency_passed():
    """Verify emergency scenarios pass if the referral decision is 'emergency'."""
    state = _mock_state(urgency_level="emergency", next_step="emergency")
    
    updates = await build_patient_response(state)
    resp = updates["patient_response"]
    
    assert resp["urgency_level"] == "emergency"
    assert "EMERGENCY" in resp["care_plan"]["immediate_actions"][0]
