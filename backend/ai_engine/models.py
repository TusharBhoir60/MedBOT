"""
Shared agent I/O Pydantic models for the CMAR framework.

These model stubs are defined in Sprint 1 to:
  1. Reserve the schema namespace so Sprint 2+ imports work cleanly
  2. Validate the BaseSchema inheritance chain with CMAR-specific fields
  3. Serve as documentation of the CMAR contract for research publication

Sprint 5 CMAR implementation will fully populate these models.
"""
from typing import Any
from schemas.base_schema import BaseSchema


class CMARAgentOutput(BaseSchema):
    """Structured output contract for all CMAR specialist agents.

    Every agent in the AarogyaAgent v2 system must return this schema.
    The CMAR Escalation Arbiter reads confidence_score from all agents
    and applies calibration-weighted voting to produce a final decision.

    Fields:
        agent_id:         Unique identifier of the producing agent
        confidence_score: Calibrated probability in [0.0, 1.0]
        triage_decision:  The agent's recommended triage outcome
        reasoning_trace:  Ordered list of reasoning steps for explainability
        metadata:         Arbitrary agent-specific audit data
    """

    agent_id: str
    confidence_score: float  # Range: [0.0, 1.0]
    triage_decision: str
    reasoning_trace: list[str]
    metadata: dict[str, Any] = {}
