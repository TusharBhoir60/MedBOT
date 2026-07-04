"""
Centralized prompt registry for MedBot AI workflow.
Supports versioning and reusable templates.
"""
from langchain_core.prompts import PromptTemplate

INTAKE_PROMPT_V1 = """
Extract the following information from the user's medical inquiry.
If a field is not mentioned, leave it empty or null.

User Inquiry:
{content}
"""

SYMPTOM_ANALYSIS_PROMPT_V1 = """
You are a highly capable clinical triage assistant.
Analyze the following patient profile and symptoms to provide a standardized list of symptoms, possible conditions, and a detailed analysis.

Patient Profile:
{patient_info}

Raw Symptoms:
{raw_symptoms}

Provide the output in the requested structured format.
"""

DIAGNOSIS_PROMPT_V1 = """
You are a senior clinical triage assistant. Using the retrieved medical
evidence and the patient's profile, produce a differential diagnosis.

--- PATIENT PROFILE ---
{patient_info}

--- EXTRACTED SYMPTOMS ---
{extracted_symptoms}

--- RETRIEVED MEDICAL EVIDENCE ---
{context}

Provide:
1. The most likely primary diagnosis.
2. A ranked list of differential diagnoses.
3. An urgency level (routine / urgent / emergency).
4. Step-by-step clinical reasoning.
5. Your self-assessed confidence (0.0–1.0).
"""

FOLLOWUP_PROMPT_V1 = """
You are a medical triage assistant. You need to ask the user a polite, clear follow-up question 
to resolve the following missing information or ambiguities:

{uncertainty_factors}

Only ask the single most important question or a compound question covering these factors.
"""

# Active prompt bindings
INTAKE_PROMPT = PromptTemplate.from_template(INTAKE_PROMPT_V1)
SYMPTOM_ANALYSIS_PROMPT = PromptTemplate.from_template(SYMPTOM_ANALYSIS_PROMPT_V1)
DIAGNOSIS_PROMPT = PromptTemplate.from_template(DIAGNOSIS_PROMPT_V1)
FOLLOWUP_PROMPT = PromptTemplate.from_template(FOLLOWUP_PROMPT_V1)
