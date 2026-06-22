# Maharashtra Validation Plan — AarogyaAgent CMAR

This document outlines the validation strategy for deploying and evaluating the AarogyaAgent system against real-world clinical data from Maharashtra, India.

---

## 1. Dataset Preparation

### 1.1 Data Sources
- De-identified patient records from Maharashtra district hospitals.
- Government of Maharashtra Health Management Information System (HMIS) aggregate data.
- Published epidemiological studies on disease prevalence in Maharashtra (dengue, malaria, hypertension, anaemia).

### 1.2 Dataset Structure

| Field | Type | Description |
|---|---|---|
| case_id | string | Unique anonymised identifier |
| age | int | Patient age |
| gender | string | Patient gender |
| reported_symptoms | list[str] | Symptoms as reported (may be vernacular) |
| confirmed_diagnosis | string | Clinician-confirmed diagnosis |
| urgency_assigned | string | Actual triage urgency |
| region | string | District/taluka |
| season | string | Monsoon / winter / summer |

### 1.3 Minimum Dataset Size
- **Target:** 500 validated cases across at least 5 conditions.
- **Split:** 70% evaluation, 15% calibration tuning, 15% holdout.

---

## 2. Sanitisation

### 2.1 PII Removal
- All patient-identifiable information (name, address, Aadhaar, phone) must be removed or hashed before ingestion.
- Dates of birth replaced with age at time of visit.

### 2.2 Data Quality Filters
- Exclude records with missing confirmed diagnosis.
- Exclude records with fewer than 2 reported symptoms.
- Flag and review records where clinician diagnosis and lab results conflict.

---

## 3. Regional Symptom Mapping

### 3.1 Vernacular → Standard Medical Term Translation

Maharashtra's population reports symptoms in Marathi, Hindi, and English. A mapping table is required.

| Vernacular (Marathi) | Vernacular (Hindi) | Standard Medical Term |
|---|---|---|
| ताप (taap) | बुखार (bukhaar) | Fever |
| डोकेदुखी (dokedukhi) | सिरदर्द (sirdard) | Headache |
| अंगदुखी (angdukhi) | शरीर दर्द (shareer dard) | Body ache / Myalgia |
| चक्कर येणे (chakkar yene) | चक्कर आना (chakkar aana) | Dizziness |
| उलटी (ulti) | उल्टी (ulti) | Vomiting |
| जुलाब (julab) | दस्त (dast) | Diarrhoea |
| थकवा (thakwa) | थकान (thakaan) | Fatigue |

### 3.2 Implementation
- Build a lookup table in `backend/data/symptom_mappings/marathi.json`.
- Integrate into the Intake Agent's pre-processing pipeline (Sprint 4+).

---

## 4. Benchmark Methodology

### 4.1 Evaluation Protocol
1. Run each case through the full CMAR pipeline (Intake → Symptom → Diagnosis).
2. Compare the system's `primary_diagnosis` against `confirmed_diagnosis`.
3. Compare the system's `urgency_level` against `urgency_assigned`.
4. Record all CMAR confidence scores for calibration analysis.

### 4.2 Metrics to Report
- Precision, Recall, F1 (per-condition and macro-averaged).
- Triage Accuracy (overall and per-urgency-level).
- Confidence Calibration (ECE, MCE).
- Retrieval Precision@k for the RAG layer.

### 4.3 Baseline Comparisons
- **Baseline 1:** LLM-only (no RAG retrieval) — measures the value of the Medical KB.
- **Baseline 2:** Keyword-matching triage rule engine — measures the value of the LLM reasoning.
- **Baseline 3:** Single-agent (no CMAR multi-agent) — measures the value of multi-agent architecture.

---

## 5. Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Data acquisition & ethics approval | 4 weeks | Signed data agreements, IRB clearance |
| Data sanitisation & mapping | 2 weeks | Clean dataset, symptom mapping table |
| Baseline evaluation | 1 week | Baseline metrics report |
| CMAR evaluation | 1 week | Full metrics report with calibration curves |
| Report & recommendations | 1 week | Final validation report |
