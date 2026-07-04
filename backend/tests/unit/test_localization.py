import pytest
from localization.localizer import Localizer
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
            evidence_bullets=["No specific guidelines were retrieved"],
            formatted_citations=["cit1"],
            confidence_explanation="high",
            differential_summary="diffs"
        ),
        care_plan=CarePlan(
            condition="Dengue",
            immediate_actions=["Seek medical consultation within 24 hours."],
            home_care=["home1"],
            diet_recommendations=["diet1"],
            lifestyle_advice=["life1"],
            warning_signs=["warn1"],
            follow_up_timeline="tmw",
            referral_recommendation="refer",
            version="v1"
        ),
        referral_decision="urgent",
        audit_trail=AuditTrail(session_id="123")
    )


def test_localizer_hindi(dummy_response):
    localizer = Localizer()
    hi_resp = localizer.translate(dummy_response, "hi-IN")
    
    assert hi_resp.language == "hi-IN"
    assert hi_resp.urgency_level == "तत्काल"
    assert "डेंगू" in hi_resp.diagnosis
    assert "कोई विशिष्ट दिशानिर्देश प्राप्त नहीं हुए" in hi_resp.explanation.evidence_bullets[0]
    assert "24 घंटे के भीतर चिकित्सा परामर्श लें।" in hi_resp.care_plan.immediate_actions[0]


def test_localizer_marathi(dummy_response):
    localizer = Localizer()
    mr_resp = localizer.translate(dummy_response, "mr-IN")
    
    assert mr_resp.language == "mr-IN"
    assert mr_resp.urgency_level == "तातडीचे"
    assert "डेंग्यू" in mr_resp.diagnosis
    assert "कोणतीही विशिष्ट मार्गदर्शक तत्त्वे प्राप्त झाली नाहीत" in mr_resp.explanation.evidence_bullets[0]
    assert "२४ तासांच्या आत वैद्यकीय सल्ला घ्या." in mr_resp.care_plan.immediate_actions[0]


def test_localizer_fallback(dummy_response):
    localizer = Localizer()
    # Unsupported locale should fallback to en-IN
    fallback_resp = localizer.translate(dummy_response, "fr-FR")
    assert fallback_resp.language == "fr-FR"
    assert fallback_resp.urgency_level == "urgent"
