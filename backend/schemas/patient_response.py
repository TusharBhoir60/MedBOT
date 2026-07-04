"""
Shared Pydantic schemas for Sprint 5 output layer.
All schemas used by explainability, care plan, audit trail, and reporting.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─── Explanation ──────────────────────────────────────────────────────────────

class ExplanationOutput(BaseModel):
    reasoning_summary: str = Field(..., description="Plain-English summary of clinical reasoning")
    evidence_bullets: List[str] = Field(default_factory=list, description="Key evidence bullet points")
    formatted_citations: List[str] = Field(default_factory=list, description="Formatted citation strings")
    confidence_explanation: str = Field(..., description="Plain-English confidence narrative")
    differential_summary: str = Field("", description="Brief summary of differential diagnoses considered")


# ─── Care Plan ────────────────────────────────────────────────────────────────

class CarePlan(BaseModel):
    condition: str
    immediate_actions: List[str] = Field(default_factory=list)
    home_care: List[str] = Field(default_factory=list)
    diet_recommendations: List[str] = Field(default_factory=list)
    lifestyle_advice: List[str] = Field(default_factory=list)
    warning_signs: List[str] = Field(default_factory=list)
    follow_up_timeline: str = Field("", description="Recommended follow-up schedule")
    referral_recommendation: str = Field("", description="Whether/where to refer patient")
    context_notes: List[str] = Field(default_factory=list, description="Age/sex/risk-specific adaptations")
    version: str = Field("v1", description="Care plan template version")


# ─── Audit Trail ──────────────────────────────────────────────────────────────

class AuditTrail(BaseModel):
    session_id: str
    workflow_version: str = "v1"
    experiment_id: Optional[str] = None
    dataset_version: Optional[str] = None
    prompt_version: str = "v1"
    care_plan_version: str = "v1"
    embedding_model: Optional[str] = None
    retrieval_top_k: Optional[int] = None
    translation_version: str = "v1"
    confidence_scores_snapshot: Dict[str, float] = Field(default_factory=dict)
    retrieved_evidence_ids: List[str] = Field(default_factory=list)
    timestamps: Dict[str, str] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─── Reporting ────────────────────────────────────────────────────────────────

class DoctorReportSection(BaseModel):
    title: str
    content: str


class DoctorReport(BaseModel):
    """Structured clinical report suitable for PDF export."""
    report_id: str
    generated_at: str
    patient_demographics: DoctorReportSection
    chief_complaint: DoctorReportSection
    clinical_reasoning: DoctorReportSection
    diagnosis: DoctorReportSection
    differential_diagnoses: DoctorReportSection
    evidence_summary: DoctorReportSection
    confidence_assessment: DoctorReportSection
    urgency_assessment: DoctorReportSection
    care_plan_summary: DoctorReportSection
    referral_recommendation: DoctorReportSection
    audit_reference: DoctorReportSection


class PatientSummary(BaseModel):
    """Simplified report for the patient (non-clinical language)."""
    summary_id: str
    generated_at: str
    what_we_found: str
    what_to_do_now: List[str]
    things_to_watch_for: List[str]
    when_to_see_a_doctor: str
    your_care_plan: List[str]
    language: str = "en-IN"


class AuditReport(BaseModel):
    """Full audit log for regulatory and research accountability."""
    report_id: str
    generated_at: str
    audit_trail: AuditTrail
    safety_checks_passed: bool
    safety_violations: List[str] = Field(default_factory=list)
    diagnosis_summary: str
    confidence_summary: str


# ─── Top-Level Patient Response ───────────────────────────────────────────────

class PatientResponse(BaseModel):
    """Complete structured output returned after a CMAR workflow run."""
    session_id: str
    diagnosis: str
    differential_diagnoses: List[str] = Field(default_factory=list)
    urgency_level: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: ExplanationOutput
    care_plan: CarePlan
    warning_signs: List[str] = Field(default_factory=list)
    referral_decision: str
    citations: List[str] = Field(default_factory=list)
    language: str = "en-IN"
    audit_trail: AuditTrail
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety_validated: bool = False
