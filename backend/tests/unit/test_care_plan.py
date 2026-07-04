import pytest
from ai_engine.care_plan.care_plan_generator import CarePlanGenerator
from ai_engine.care_plan.care_plan_library import StaticCarePlanLibrary


def test_care_plan_dengue():
    gen = CarePlanGenerator()
    diag = {"primary_diagnosis": "Dengue fever", "urgency_level": "urgent"}
    
    plan = gen.generate(diag, {})
    assert plan.condition == "Dengue fever"
    assert "dengue" in str(plan.diet_recommendations).lower() or "papaya" in str(plan.diet_recommendations).lower()
    assert "Visit a clinic" in plan.immediate_actions[0]  # urgent adaptation


def test_care_plan_context_adaptations():
    gen = CarePlanGenerator()
    diag = {"primary_diagnosis": "Malaria", "urgency_level": "routine"}
    patient = {"age": 4, "gender": "F", "risk_factors": ["Diabetes"]}
    
    plan = gen.generate(diag, patient)
    notes = " ".join(plan.context_notes).lower()
    
    assert "child under 5" in notes
    assert "female" in notes or "pregnancy" in notes
    assert "diabetic" in notes or "blood glucose" in notes


def test_care_plan_emergency():
    gen = CarePlanGenerator()
    diag = {"primary_diagnosis": "Stroke", "urgency_level": "emergency"}
    
    plan = gen.generate(diag, {})
    assert "EMERGENCY" in plan.immediate_actions[0]
    assert "EMERGENCY" in plan.referral_recommendation


def test_care_plan_unsupported():
    gen = CarePlanGenerator()
    diag = {"primary_diagnosis": "RareDiseaseX", "urgency_level": "routine"}
    
    plan = gen.generate(diag, {})
    # Generic fallback
    assert "RareDiseaseX" == plan.condition
    assert "balanced diet" in str(plan.diet_recommendations).lower()
