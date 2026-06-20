"""
AI Engine package — scaffold for Sprint 2+ LangGraph and CMAR implementation.

This package is intentionally empty in Sprint 1. Its presence reserves
the namespace and establishes the package boundary so that Sprint 2+
imports (e.g., `from ai_engine.agents import SymptomAgent`) work
without restructuring.

Planned Sprint 2+ structure:
    ai_engine/
    ├── agents/        — Individual specialist agent implementations
    │   ├── symptom_agent.py
    │   ├── triage_agent.py
    │   └── escalation_agent.py
    ├── confidence/    — Confidence scoring and calibration logic
    ├── graphs/        — LangGraph StateGraph compilation and workflow definitions
    │   ├── triage_graph.py
    │   └── cmar_graph.py
    ├── models.py      — Shared agent input/output Pydantic schemas
    ├── prompts/       — Prompt templates for agents
    ├── rag/           — Retrieval-Augmented Generation (RAG) components
    └── state/         — State definitions for LangGraph workflows
"""
