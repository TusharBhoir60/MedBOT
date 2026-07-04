"""
Orchestrator node for assembling the final PatientResponse.
"""
import logging
from typing import Any, Dict

from ai_engine.state import SharedState
from ai_engine.explainability.patient_explainer import PatientExplainer
from ai_engine.care_plan.care_plan_generator import CarePlanGenerator
from ai_engine.audit.audit_trail import AuditTrailBuilder
from ai_engine.safety.response_validator import ResponseValidator
from localization.localizer import Localizer
from schemas.patient_response import PatientResponse

logger = logging.getLogger(__name__)

class PatientResponseBuilder:
    """
    Constructs the final PatientResponse by orchestrating Sprint 5 modules.
    """

    def __init__(self):
        self.explainer = PatientExplainer()
        self.care_plan_generator = CarePlanGenerator()
        self.audit_builder = AuditTrailBuilder()
        self.validator = ResponseValidator()
        self.localizer = Localizer()

    async def build(self, state: SharedState) -> Dict[str, Any]:
        """
        Builds the PatientResponse and updates the state.
        """
        logger.info("Building final PatientResponse...")
        
        diag_out = state.get("diagnosis_output", {})
        scores = state.get("confidence_scores", {})
        patient_info = state.get("patient_info", {})
        session_id = state.get("session_id", "unknown-session")
        citations = state.get("citations", [])

        # 1. Explainability
        explanation = self.explainer.explain(diag_out, scores)
        
        # 2. Care Plan
        care_plan = self.care_plan_generator.generate(diag_out, patient_info)
        
        # 3. Audit Trail
        audit_trail = self.audit_builder.build(
            session_id=session_id,
            confidence_scores=scores,
            citations=citations
        )
        
        # 4. Construct PatientResponse
        response = PatientResponse(
            session_id=session_id,
            diagnosis=diag_out.get("primary_diagnosis", "Unknown"),
            differential_diagnoses=diag_out.get("differential_diagnoses", []),
            urgency_level=diag_out.get("urgency_level", "routine"),
            confidence=float(diag_out.get("diagnosis_confidence", 0.0)),
            explanation=explanation,
            care_plan=care_plan,
            warning_signs=care_plan.warning_signs,
            referral_decision=diag_out.get("next_step", "end"),
            citations=citations,
            audit_trail=audit_trail
        )
        
        # 5. Safety Validation
        # This will raise a SafetyViolation if critical invariants are breached.
        response = self.validator.validate_or_raise(response)
        response.safety_validated = True
        
        # 6. Localization
        # If the API provided a language preference in patient_info, we use it, else en-IN.
        target_locale = patient_info.get("language", "en-IN")
        localized_response = self.localizer.translate(response, target_locale)
        
        # Return state updates
        return {
            "explanation": explanation.model_dump(),
            "care_plan": care_plan.model_dump(),
            "audit_trail": audit_trail.model_dump(),
            "patient_response": localized_response.model_dump(),
        }

# For LangGraph node integration
_builder = PatientResponseBuilder()

async def build_patient_response(state: SharedState) -> Dict[str, Any]:
    return await _builder.build(state)
