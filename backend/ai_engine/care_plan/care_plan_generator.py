"""
Context-aware CarePlanGenerator.
Takes diagnosis_output + patient_info and returns a fully personalised CarePlan.
Context dimensions: age, sex, risk_factors, urgency, diagnosis.
"""
from typing import Any, Dict, List, Optional

from schemas.patient_response import CarePlan
from ai_engine.care_plan.care_plan_provider import CarePlanProvider
from ai_engine.care_plan.care_plan_library import StaticCarePlanLibrary


class CarePlanGenerator:
    """
    Generates a context-aware CarePlan by:
    1. Fetching a base plan from a CarePlanProvider
    2. Applying age / sex / risk-factor / urgency adaptations
    """

    def __init__(self, provider: Optional[CarePlanProvider] = None) -> None:
        self._provider: CarePlanProvider = provider or StaticCarePlanLibrary()

    def generate(
        self,
        diagnosis_output: Dict[str, Any],
        patient_info: Dict[str, Any] = None,
    ) -> CarePlan:
        if patient_info is None:
            patient_info = {}

        condition = diagnosis_output.get("primary_diagnosis", "Unknown")
        urgency = diagnosis_output.get("urgency_level", "routine")

        # Fetch base plan
        base_plan = self._provider.get_plan(condition)

        # Context fields
        age: Optional[int] = patient_info.get("age")
        sex: str = patient_info.get("gender", patient_info.get("sex", "")).lower()
        risk_factors: List[str] = patient_info.get("risk_factors", [])

        context_notes: List[str] = []

        # ── Age adaptations ──────────────────────────────────────────────────
        if age is not None:
            if age < 5:
                context_notes.append(
                    "Child under 5: dose all medications by weight. Prioritise hospital referral."
                )
            elif age < 12:
                context_notes.append(
                    "Paediatric patient: ensure paediatric dosing. Involve parents in all care decisions."
                )
            elif age >= 65:
                context_notes.append(
                    "Elderly patient (≥65): higher risk of complications. Consider early referral."
                )
                context_notes.append(
                    "Review for polypharmacy interactions with current medications."
                )

        # ── Sex adaptations ───────────────────────────────────────────────────
        if sex in ("f", "female"):
            if condition.lower() in ("dengue", "malaria", "anemia"):
                context_notes.append(
                    "Female patient: consider pregnancy status. Some medications contraindicated in pregnancy."
                )
        if sex in ("m", "male") and condition.lower() == "hypertension":
            context_notes.append(
                "Male patient with hypertension: assess for additional cardiovascular risk factors."
            )

        # ── Risk factor adaptations ───────────────────────────────────────────
        rf_lower = [r.lower() for r in risk_factors]
        if any(r in rf_lower for r in ("diabetes", "diabetic")):
            context_notes.append(
                "Diabetic patient: monitor blood glucose closely; infection can destabilise control."
            )
        if any(r in rf_lower for r in ("smoking", "smoker")):
            context_notes.append(
                "Smoker: smoking cessation is strongly recommended for cardiovascular and pulmonary health."
            )
        if any(r in rf_lower for r in ("pregnant", "pregnancy")):
            context_notes.append(
                "Pregnant patient: consult obstetrician before any medication change."
            )
        if any(r in rf_lower for r in ("hypertension", "htn")):
            context_notes.append(
                "Pre-existing hypertension: extra caution with NSAIDs and decongestants."
            )
        if any(r in rf_lower for r in ("immunocompromised", "hiv", "aids")):
            context_notes.append(
                "Immunocompromised patient: higher risk of severe disease — early hospital referral advised."
            )

        # ── Urgency adaptations ───────────────────────────────────────────────
        immediate = list(base_plan.immediate_actions)
        referral = base_plan.referral_recommendation

        if urgency == "emergency":
            immediate.insert(0, "⚠ EMERGENCY: Go to the nearest hospital immediately or call 108.")
            referral = "EMERGENCY referral — activate hospital protocol now."
        elif urgency == "urgent":
            immediate.insert(0, "Visit a clinic or hospital within 2–4 hours.")

        # Build final plan with contextual additions
        return CarePlan(
            condition=condition,
            immediate_actions=immediate,
            home_care=base_plan.home_care,
            diet_recommendations=base_plan.diet_recommendations,
            lifestyle_advice=base_plan.lifestyle_advice,
            warning_signs=base_plan.warning_signs,
            follow_up_timeline=base_plan.follow_up_timeline,
            referral_recommendation=referral,
            context_notes=context_notes,
            version=base_plan.version,
        )
