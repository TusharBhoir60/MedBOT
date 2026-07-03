"""
Safety validation layer: validates PatientResponse for schema consistency
and clinical output integrity before returning to the caller.
"""
from typing import Any, Dict, List, Tuple

from schemas.patient_response import PatientResponse, CarePlan, ExplanationOutput


class SafetyViolation(Exception):
    """Raised when a blocking safety rule is violated."""
    pass


class ResponseValidator:
    """
    Validates a PatientResponse before it is returned to the API layer.

    Checks performed:
    1. Confidence floor  — confidence must be a valid float in [0, 1]
    2. Emergency care plan — emergency urgency must trigger ER referral
    3. Warning signs present — non-routine cases must have warning signs
    4. Explanation populated — reasoning_summary must not be empty
    5. Care plan populated  — care plan must have at least one immediate action
    6. Session ID present   — audit trail must have a valid session ID
    """

    # Urgency levels that require an ER referral recommendation
    _EMERGENCY_URGENCIES = {"emergency"}

    def validate(self, response: PatientResponse) -> Tuple[bool, List[str]]:
        """
        Validate the response.
        Returns (is_valid, [violation_messages]).
        Violations are warnings; only BLOCKING violations raise SafetyViolation.
        """
        violations: List[str] = []

        # 1. Confidence range
        if not (0.0 <= response.confidence <= 1.0):
            violations.append(f"Confidence {response.confidence} is outside [0, 1].")

        # 2. Emergency urgency must include ER referral
        if response.urgency_level.lower() in self._EMERGENCY_URGENCIES:
            referral_lower = response.referral_decision.lower()
            plan_referral = response.care_plan.referral_recommendation.lower()
            if "emergency" not in referral_lower and "emergency" not in plan_referral:
                violations.append(
                    "Emergency urgency detected but referral_decision does not indicate emergency referral."
                )

        # 3. Warning signs for non-routine cases
        if response.urgency_level.lower() != "routine" and not response.care_plan.warning_signs:
            violations.append(
                f"Urgency is '{response.urgency_level}' but no warning signs are populated."
            )

        # 4. Explanation must be populated
        if not response.explanation.reasoning_summary.strip():
            violations.append("reasoning_summary is empty — explanation was not generated.")

        # 5. Care plan must have at least one immediate action
        if not response.care_plan.immediate_actions:
            violations.append("Care plan has no immediate_actions.")

        # 6. Session ID must be present
        if not response.audit_trail.session_id.strip():
            violations.append("audit_trail.session_id is missing or empty.")

        is_valid = len(violations) == 0
        return is_valid, violations

    def validate_or_raise(self, response: PatientResponse) -> PatientResponse:
        """Validates and raises SafetyViolation if any violations found."""
        ok, violations = self.validate(response)
        if not ok:
            raise SafetyViolation(
                f"PatientResponse failed safety validation: {'; '.join(violations)}"
            )
        return response
