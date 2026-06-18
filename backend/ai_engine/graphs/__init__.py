"""
Graphs sub-package — Sprint 2+ LangGraph StateGraph compilation.

StateGraphs are compiled here and exposed as async callables to the
service layer. The service layer calls the compiled graph without
any direct LangGraph coupling in the API layer.

Planned graphs:
    triage_graph.py   — Full CMAR triage workflow orchestration
    cmar_graph.py     — Confidence-Weighted Multi-Agent Reasoning arbiter
"""
