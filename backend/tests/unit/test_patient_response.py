import pytest
from ai_engine.safety.response_validator import ResponseValidator, SafetyViolation
from schemas.patient_response import PatientResponse, CarePlan, ExplanationOutput, AuditTrail


@pytest.fixture
def valid_response():
    return PatientResponse(
        session_id="123",
        diagnosis="Dengue",
        urgency_level="routine",
        confidence=0.85,
        explanation=ExplanationOutput(
            reasoning_summary="Valid reasoning summary.",
            evidence_bullets=[],
            formatted_citations=[],
            confidence_explanation="high",
            differential_summary=""
        ),
        care_plan=CarePlan(
            condition="Dengue",
            immediate_actions=["Drink fluids"],
            warning_signs=[],
            version="v1"
        ),
        referral_decision="routine_checkup",
        audit_trail=AuditTrail(session_id="123")
    )


def test_validator_happy_path(valid_response):
    validator = ResponseValidator()
    ok, violations = validator.validate(valid_response)
    assert ok is True
    assert len(violations) == 0


def test_validator_emergency_consistency(valid_response):
    valid_response.urgency_level = "emergency"
    valid_response.care_plan.warning_signs = ["Loss of consciousness"]
    # Referral decision not ER -> violation
    valid_response.referral_decision = "routine_checkup"
    
    validator = ResponseValidator()
    ok, violations = validator.validate(valid_response)
    
    assert ok is False
    assert any("referral_decision" in v for v in violations)


def test_validator_missing_explanation(valid_response):
    valid_response.explanation.reasoning_summary = "   "
    validator = ResponseValidator()
    ok, violations = validator.validate(valid_response)
    
    assert ok is False
    assert any("empty" in v for v in violations)


def test_validator_missing_session_id(valid_response):
    valid_response.audit_trail.session_id = ""
    validator = ResponseValidator()
    ok, violations = validator.validate(valid_response)
    
    assert ok is False
    assert any("session_id" in v for v in violations)


def test_validator_raises(valid_response):
    valid_response.confidence = 1.5
    validator = ResponseValidator()
    with pytest.raises(SafetyViolation):
        validator.validate_or_raise(valid_response)
