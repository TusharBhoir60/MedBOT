"""
StaticCarePlanLibrary: condition-specific care plan templates for
Dengue, Malaria, Hypertension, Anemia, and Emergency scenarios.
"""
from typing import Dict

from schemas.patient_response import CarePlan
from ai_engine.care_plan.care_plan_provider import CarePlanProvider


# Raw template data — keyed by normalised condition name
_TEMPLATES: Dict[str, dict] = {
    "dengue": {
        "immediate_actions": [
            "Seek medical consultation within 24 hours.",
            "Get a complete blood count (CBC) test immediately.",
            "Do not take aspirin or ibuprofen (NSAIDs) — risk of bleeding.",
        ],
        "home_care": [
            "Rest completely for at least 5–7 days.",
            "Drink at least 2–3 litres of fluids daily (ORS, coconut water, juices).",
            "Monitor body temperature every 4 hours.",
            "Use paracetamol only for fever management.",
        ],
        "diet_recommendations": [
            "Soft, easily digestible foods such as khichdi, dal, soups.",
            "High fluid intake — ORS, fresh juices, coconut water.",
            "Avoid fried, spicy, or oily foods during fever.",
            "Papaya leaf extract may help raise platelet count (evidence limited).",
        ],
        "lifestyle_advice": [
            "Use mosquito nets and repellent at all times.",
            "Wear full-sleeved clothing.",
            "Eliminate standing water around the home.",
            "Avoid strenuous activity until platelet count normalises.",
        ],
        "warning_signs": [
            "Bleeding from gums, nose, or in stool/urine.",
            "Severe abdominal pain or persistent vomiting.",
            "Rapid breathing or difficulty breathing.",
            "Extreme fatigue or altered consciousness.",
            "Platelet count below 100,000/μL.",
        ],
        "follow_up_timeline": "Daily monitoring of platelet count. Follow-up with physician within 48 hours or sooner if warning signs appear.",
        "referral_recommendation": "Refer to hospital if platelet count drops below 100,000/μL or warning signs appear.",
    },
    "malaria": {
        "immediate_actions": [
            "Rapid diagnostic test (RDT) or blood smear immediately.",
            "Start anti-malarial treatment as prescribed (artemisinin-based therapy).",
            "Do NOT delay treatment — malaria can become severe within hours.",
        ],
        "home_care": [
            "Complete the full course of anti-malarial medication.",
            "Rest and maintain hydration.",
            "Monitor for recurrence of fever in the next 7 days.",
        ],
        "diet_recommendations": [
            "High calorie, easily digestible meals.",
            "Plenty of fluids — ORS, soups, fruit juices.",
            "Iron-rich foods to counter anaemia: lentils, spinach, jaggery.",
        ],
        "lifestyle_advice": [
            "Sleep under insecticide-treated mosquito nets.",
            "Use mosquito repellent on exposed skin.",
            "Wear protective clothing at dawn and dusk.",
        ],
        "warning_signs": [
            "High fever >40°C unresponsive to medication.",
            "Altered consciousness or seizures.",
            "Severe anaemia or jaundice.",
            "Black/dark urine (blackwater fever).",
            "Inability to take oral medication.",
        ],
        "follow_up_timeline": "Return for blood smear check after completing treatment (Day 3 and Day 28).",
        "referral_recommendation": "Refer to hospital immediately for severe malaria features or treatment failure.",
    },
    "hypertension": {
        "immediate_actions": [
            "Measure blood pressure both arms and record.",
            "If BP >180/110 mmHg with symptoms, go to emergency immediately.",
            "Do not stop current antihypertensive medications abruptly.",
        ],
        "home_care": [
            "Home BP monitoring twice daily (morning and evening).",
            "Take all medications as prescribed without missing doses.",
            "Reduce work-related or emotional stress.",
        ],
        "diet_recommendations": [
            "DASH diet: fruits, vegetables, low-fat dairy, whole grains.",
            "Limit sodium to <2.3 g/day (avoid pickles, papad, processed foods).",
            "Avoid alcohol; limit caffeinated beverages.",
            "Increase potassium-rich foods: bananas, potatoes, spinach.",
        ],
        "lifestyle_advice": [
            "30 minutes of moderate aerobic exercise 5 days/week (walking, cycling).",
            "Achieve/maintain healthy body weight (BMI 18.5–24.9).",
            "Stop smoking — nicotine acutely raises BP.",
            "Limit screen time and ensure 7–8 hours sleep.",
        ],
        "warning_signs": [
            "Severe headache, especially at back of head.",
            "Blurred vision or sudden visual changes.",
            "Chest pain or shortness of breath.",
            "Sudden weakness or numbness in face/arm/leg.",
            "BP reading >180/120 mmHg.",
        ],
        "follow_up_timeline": "Review with physician in 1–2 weeks if newly diagnosed. Monthly follow-up once stable.",
        "referral_recommendation": "Refer to cardiologist if BP uncontrolled on 3 medications or target organ damage suspected.",
    },
    "anemia": {
        "immediate_actions": [
            "Complete blood count (CBC) with peripheral smear.",
            "Identify and treat underlying cause (nutritional, haemolytic, blood loss).",
            "Do not self-medicate with iron supplements without diagnosis confirmation.",
        ],
        "home_care": [
            "Take iron/folate/B12 supplements as prescribed.",
            "Avoid tea or coffee within 1 hour of iron tablet intake (inhibits absorption).",
            "Take iron with vitamin C source (lemon water, orange juice) to enhance absorption.",
        ],
        "diet_recommendations": [
            "Iron-rich foods: red meat, liver, lentils, spinach, jaggery, fortified cereals.",
            "Vitamin C-rich foods with each meal: amla, guava, tomatoes, citrus.",
            "Folate: leafy greens, beans, fortified grains.",
            "Vitamin B12: eggs, dairy, meat (or B12-fortified foods for vegetarians).",
        ],
        "lifestyle_advice": [
            "Avoid vigorous exercise until haemoglobin normalises.",
            "Rest when fatigued; avoid overexertion.",
            "Cook in iron vessels (may increase dietary iron intake).",
        ],
        "warning_signs": [
            "Haemoglobin below 7 g/dL — may need transfusion.",
            "Chest pain or palpitations at rest.",
            "Severe breathlessness on minimal exertion.",
            "Fainting or loss of consciousness.",
            "Yellow/pale skin with dark urine (haemolysis).",
        ],
        "follow_up_timeline": "Recheck haemoglobin after 4 weeks of treatment. Monthly until normal.",
        "referral_recommendation": "Refer to haematologist if Hb <7 g/dL, or if cause unclear after initial workup.",
    },
    "emergency": {
        "immediate_actions": [
            "Call emergency services (108 in India) immediately.",
            "Do NOT leave the patient alone.",
            "If cardiac arrest: begin CPR if trained.",
            "If stroke: note time of symptom onset — critical for thrombolysis window.",
        ],
        "home_care": [
            "No home care — emergency hospital admission required.",
            "Keep the patient calm and still until help arrives.",
        ],
        "diet_recommendations": [
            "Nothing by mouth (NPO) until evaluated by emergency physician.",
        ],
        "lifestyle_advice": [
            "This is a medical emergency. Follow emergency team instructions.",
        ],
        "warning_signs": [
            "Loss of consciousness.",
            "Difficulty breathing or no breathing.",
            "Absence of pulse.",
            "Severe chest pain radiating to arm/jaw.",
            "Sudden severe headache, facial drooping, arm weakness (stroke).",
        ],
        "follow_up_timeline": "Hospital emergency department — immediate admission required.",
        "referral_recommendation": "Emergency department referral — activate ambulance now.",
    },
}

# Normalisation aliases for fuzzy matching
_ALIASES: Dict[str, str] = {
    "emergency (cardiac)": "emergency",
    "cardiac emergency": "emergency",
    "stroke": "emergency",
    "acute myocardial infarction": "emergency",
    "heart attack": "emergency",
    "dengue fever": "dengue",
    "plasmodium falciparum malaria": "malaria",
    "plasmodium vivax malaria": "malaria",
    "iron deficiency anemia": "anemia",
    "iron deficiency anaemia": "anemia",
    "nutritional anaemia": "anemia",
    "essential hypertension": "hypertension",
    "high blood pressure": "hypertension",
}


def _normalise(condition: str) -> str:
    lower = condition.strip().lower()
    return _ALIASES.get(lower, lower)


class StaticCarePlanLibrary(CarePlanProvider):
    """
    Static evidence-based care plan templates for supported conditions.
    Acts as the default CarePlanProvider implementation.
    """

    def supports(self, condition: str) -> bool:
        return _normalise(condition) in _TEMPLATES

    def get_plan(self, condition: str) -> CarePlan:
        key = _normalise(condition)
        tmpl = _TEMPLATES.get(key)
        if tmpl is None:
            return self._generic_plan(condition)
        return CarePlan(condition=condition, version="v1", **tmpl)

    def _generic_plan(self, condition: str) -> CarePlan:
        return CarePlan(
            condition=condition,
            immediate_actions=["Consult a healthcare provider as soon as possible."],
            home_care=["Rest and stay hydrated.", "Monitor symptoms and note any changes."],
            diet_recommendations=["Maintain a balanced diet.", "Drink adequate fluids."],
            lifestyle_advice=["Avoid strenuous activity.", "Follow prescribed medications."],
            warning_signs=[
                "Worsening symptoms.",
                "High fever (>38.5°C) not responding to paracetamol.",
                "Difficulty breathing.",
                "Chest pain.",
            ],
            follow_up_timeline="Consult a physician within 24–48 hours.",
            referral_recommendation="Seek medical care if symptoms worsen or new symptoms appear.",
            version="v1",
        )
