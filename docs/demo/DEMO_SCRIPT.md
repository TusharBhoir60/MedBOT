# AarogyaAgent Demo Script

**Target Audience:** Judges, Investors, Hiring Managers
**Duration:** 5-7 Minutes

## 1. Introduction (1 min)
*Screen: Landing Page*
**Speaker:** "Welcome to AarogyaAgent v2. Healthcare systems worldwide are buckling under triage loads, leading to burnout and missed critical diagnoses. AarogyaAgent solves this by acting as an autonomous, AI-driven digital front door that performs clinical triage using a unique Confidence-Weighted Multi-Agent Reasoning (CMAR) architecture."

## 2. Patient Workflow & AI Reasoning (2 mins)
*Screen: Patient Chat Interface*
**Speaker:** "Let's assume the role of a patient. I'll type: 'I have a severe headache and fever.' Behind the scenes, our FastAPI backend routes this to a LangGraph workflow.
1. The **Intake Agent** collects my demographic data.
2. The **Symptom Agent** extracts 'headache' and 'fever', standardizing them.
3. The **Diagnosis Agent** queries our ChromaDB vector store, pulling in real WHO guidelines using RAG, and formulates a differential diagnosis (e.g., Dengue Fever).
But here is the innovation: The AI quantitatively scores its own confidence. If the case is too ambiguous, it refuses to hallucinate and instead triggers a Human-in-the-Loop handoff."

## 3. Physician Dashboard & HITL (2 mins)
*Screen: Physician Dashboard - Review Queue*
**Speaker:** "Let's switch to the physician's view. Here in our Next.js protected dashboard, we see the task that was just escalated.
The physician doesn't just see the final answer; they see the entire Explainability (XAI) trail. They see exactly which guidelines the RAG pipeline pulled and why the AI routed it here. The physician can quickly approve or modify the diagnosis, saving crucial time while maintaining clinical safety."

## 4. Analytics & System Health (1 min)
*Screen: Analytics Dashboard & System Health*
**Speaker:** "All this activity is aggregated in real-time. Hospital administrators can monitor system health, average AI confidence, and triage velocity through our TanStack Query powered analytics views."

## 5. Conclusion (1 min)
**Speaker:** "AarogyaAgent v2 isn't just a wrapper around an LLM. It's a scalable, secure, and deterministic medical reasoning engine ready for production deployment. Thank you."
