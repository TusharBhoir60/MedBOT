"""
Agents sub-package — Sprint 2+ specialist agent implementations.

Agents will follow the LangGraph node pattern:
  async def agent_node(state: TriageState) -> dict[str, Any]: ...

Each agent produces a CMARAgentOutput (defined in ai_engine/models.py)
carrying a confidence_score, reasoning_trace, and metadata dict.
The correlation ID from core.context propagates through all agent calls.
"""
