"""
ReportBuilder: generates DoctorReport, PatientSummary, and AuditReport
from a validated PatientResponse.
"""
import uuid
from datetime import datetime, timezone
from typing import List

from schemas.patient_response import (
    AuditReport,
    DoctorReport,
    DoctorReportSection,
    PatientResponse,
    PatientSummary,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReportBuilder:
    """Builds structured clinical reports from a PatientResponse."""

    def build_doctor_report(self, response: PatientResponse) -> DoctorReport:
        """
        Produces a section-structured DoctorReport suitable for PDF export.
        Each section maps to a discrete clinical domain.
        """
        audit = response.audit_trail
        cp = response.care_plan
        expl = response.explanation

        return DoctorReport(
            report_id=f"DR-{uuid.uuid4().hex[:8].upper()}",
            generated_at=_now(),
            patient_demographics=DoctorReportSection(
                title="Patient Demographics",
                content=f"Session ID: {response.session_id}\nLanguage: {response.language}",
            ),
            chief_complaint=DoctorReportSection(
                title="Chief Complaint / Presenting Symptoms",
                content="Derived from patient intake. See session record for full symptom log.",
            ),
            clinical_reasoning=DoctorReportSection(
                title="Clinical Reasoning",
                content=expl.reasoning_summary,
            ),
            diagnosis=DoctorReportSection(
                title="Primary Diagnosis",
                content=f"{response.diagnosis} (confidence: {int(response.confidence * 100)}%)",
            ),
            differential_diagnoses=DoctorReportSection(
                title="Differential Diagnoses",
                content=expl.differential_summary,
            ),
            evidence_summary=DoctorReportSection(
                title="Evidence Summary",
                content="\n".join(expl.evidence_bullets) or "No evidence retrieved.",
            ),
            confidence_assessment=DoctorReportSection(
                title="Confidence Assessment",
                content=expl.confidence_explanation,
            ),
            urgency_assessment=DoctorReportSection(
                title="Urgency Assessment",
                content=f"Urgency level: {response.urgency_level.upper()}",
            ),
            care_plan_summary=DoctorReportSection(
                title="Care Plan Summary",
                content="\n".join(
                    [f"Immediate: {', '.join(cp.immediate_actions[:3])}"]
                    + ([f"Follow-up: {cp.follow_up_timeline}"] if cp.follow_up_timeline else [])
                ),
            ),
            referral_recommendation=DoctorReportSection(
                title="Referral Recommendation",
                content=cp.referral_recommendation or response.referral_decision,
            ),
            audit_reference=DoctorReportSection(
                title="Audit Reference",
                content=(
                    f"Session: {audit.session_id} | "
                    f"Workflow: {audit.workflow_version} | "
                    f"Prompt: {audit.prompt_version}"
                ),
            ),
        )

    def build_patient_summary(self, response: PatientResponse) -> PatientSummary:
        """Produces a plain-language summary intended for the patient."""
        cp = response.care_plan
        return PatientSummary(
            summary_id=f"PS-{uuid.uuid4().hex[:8].upper()}",
            generated_at=_now(),
            what_we_found=(
                f"Based on your symptoms, the most likely condition is "
                f"{response.diagnosis}. {response.explanation.reasoning_summary}"
            ),
            what_to_do_now=cp.immediate_actions[:5],
            things_to_watch_for=cp.warning_signs[:6],
            when_to_see_a_doctor=cp.follow_up_timeline,
            your_care_plan=(
                cp.home_care[:3]
                + cp.diet_recommendations[:2]
                + cp.lifestyle_advice[:2]
            ),
            language=response.language,
        )

    def build_audit_report(
        self,
        response: PatientResponse,
        safety_passed: bool,
        violations: List[str] = None,
    ) -> AuditReport:
        """Produces a regulatory-grade audit report."""
        return AuditReport(
            report_id=f"AR-{uuid.uuid4().hex[:8].upper()}",
            generated_at=_now(),
            audit_trail=response.audit_trail,
            safety_checks_passed=safety_passed,
            safety_violations=violations or [],
            diagnosis_summary=(
                f"Diagnosis: {response.diagnosis} | "
                f"Urgency: {response.urgency_level} | "
                f"Confidence: {int(response.confidence * 100)}%"
            ),
            confidence_summary=response.explanation.confidence_explanation,
        )
