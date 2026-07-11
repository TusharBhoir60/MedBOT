# Judge / Interviewer Q&A Prep

This document anticipates technical and product questions from judges, recruiters, or technical reviewers.

### Q: Why use LangGraph instead of a standard OpenAI API call?
**A:** Healthcare requires deterministic routing and auditability. A standard LLM API call is a black box. LangGraph allows us to break the reasoning down into discrete nodes (Intake -> Symptom -> Diagnosis). This lets us inspect the state at every step, inject RAG data precisely where needed, and most importantly, force the system to route to a human if confidence drops, rather than hallucinating an answer.

### Q: How do you handle hallucinations in medical advice?
**A:** Three ways:
1. **RAG Grounding:** The AI is instructed to only use the medical guidelines retrieved from ChromaDB.
2. **CMAR Architecture:** The AI self-scores its confidence. If it lacks data, the confidence drops below a threshold, triggering a hard fallback to the `handoff` node (Human-in-the-loop).
3. **Safety Validators:** Hardcoded Python validators scan the LLM output for emergency keywords and block responses that attempt to diagnose life-threatening conditions autonomously.

### Q: Why Next.js and FastAPI instead of a monolith?
**A:** Separation of concerns. Next.js provides the best ecosystem for a dynamic React frontend (Tailwind, shadcn, TanStack Query), while Python is the undisputed king of AI engineering (LangChain/LangGraph). Connecting them via a REST API ensures both can scale independently.

### Q: How is the system tested?
**A:** The backend enforces a 100% pass-rate on a suite of >130 Pytest asynchronous unit and integration tests. We use a SQLite SAVEPOINT pattern to ensure zero database cross-contamination during testing. The frontend uses Playwright for End-to-End browser testing.

### Q: Is the application production ready?
**A:** Yes. The application is containerized with Docker using multi-stage builds. It implements JWT stateless authentication, RBAC, Kubernetes-ready health probes, and is continuously integrated via GitHub Actions.
