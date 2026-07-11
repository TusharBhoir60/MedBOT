# User Guide

Welcome to AarogyaAgent v2. This guide explains how to use the system from both the Patient and Physician perspectives.

## 1. Patient Workflow

### Starting a Chat
1. Navigate to the homepage.
2. Click **"Start Assessment"** to open the chat interface.
3. The AI will ask for basic demographics (Age, Gender, Location) to calibrate its medical risk models.

### Reporting Symptoms
- Describe your symptoms naturally (e.g., "I've had a headache and fever for 3 days").
- The AI will map your description to standardized medical terms and ask clarifying follow-up questions if the information is ambiguous.
- **Emergency Detection:** If you report critical symptoms (e.g., chest pain, shortness of breath), the AI will immediately halt the assessment and instruct you to seek emergency medical care.

### Receiving Results
- If the AI is highly confident in its assessment, it will provide a differential diagnosis and recommended next steps.
- If the AI requires human verification, your case will be seamlessly forwarded to a physician for review.

## 2. Physician Workflow

### Accessing the Dashboard
1. Navigate to `/login` and authenticate with your physician credentials.
2. Upon login, you will be redirected to the secure **Physician Dashboard**.

### Reviewing Tasks
1. Click on the **Review Queue** tab.
2. Select a pending task to view the patient's full conversation history, extracted symptoms, and the AI's preliminary differential diagnosis.
3. Review the AI's "Explainability (XAI)" trail to see exactly why it formulated its specific diagnosis.
4. **Approve, Modify, or Reject:** Add clinical notes and submit your final decision. The patient's record is updated automatically.

### System Analytics
1. Navigate to the **Analytics** tab.
2. View real-time metrics regarding patient intake volumes, average AI confidence scores, and task resolution times.

## 3. Administrator Workflow

### System Health
1. Navigate to the **System Health** tab.
2. Monitor the active connection status of the PostgreSQL database, ChromaDB vector store, and OpenAI LLM provider.

## 4. Known Limitations
- The system currently only supports English interactions. Multilingual support is on the future roadmap.
- The AI's differential diagnosis is for triage and informational purposes only and does not replace a formal medical diagnosis.
