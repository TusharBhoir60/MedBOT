import pytest
from ai_engine.reporting.report_builder import ReportBuilder
from schemas.patient_response import PatientResponse, CarePlan, ExplanationOutput, AuditTrail


@pytest.fixture
def dummy_response():
    return PatientResponse(
        session_id="123",
        diagnosis="Dengue",
        urgency_level="urgent",
        confidence=0.85,
        explanation=ExplanationOutput(
            reasoning_summary="summary",
            evidence_bullets=["bullet1"],
            formatted_citations=["cit1"],
            confidence_explanation="high",
            differential_summary="diffs"
        ),
        care_plan=CarePlan(
            condition="Dengue",
            immediate_actions=["act1"],
            home_care=["home1"],
            diet_recommendations=["diet1"],
            lifestyle_advice=["life1"],
            warning_signs=["warn1"],
            follow_up_timeline="tmw",
            referral_recommendation="refer",
            version="v1"
        ),
        referral_decision="refer",
        audit_trail=AuditTrail(session_id="123")
    )


def test_doctor_report(dummy_response):
    builder = ReportBuilder()
    report = builder.build_doctor_report(dummy_response)
    
    assert report.report_id.startswith("DR-")
    assert "Dengue" in report.diagnosis.content
    assert "85%" in report.diagnosis.content
    assert "summary" in report.clinical_reasoning.content


def test_patient_summary(dummy_response):
    builder = ReportBuilder()
    summary = builder.build_patient_summary(dummy_response)
    
    assert summary.summary_id.startswith("PS-")
    assert "Dengue" in summary.what_we_found
    assert "act1" in summary.what_to_do_now


def test_audit_report(dummy_response):
    builder = ReportBuilder()
    report = builder.build_audit_report(dummy_response, safety_passed=True, violations=[])
    
    assert report.report_id.startswith("AR-")
    assert report.safety_checks_passed is True
    assert "Dengue" in report.diagnosis_summary
