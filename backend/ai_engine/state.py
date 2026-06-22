"""
Shared state schemas for the LangGraph AI workflow.
Implements the CMAR (Confidence-Weighted Multi-Agent Reasoning) state.
"""
from typing import Annotated, Any, Dict, List, TypedDict
import operator
from pydantic import BaseModel, Field

class ConfidenceSchema(BaseModel):
    """Schema for individual agent confidence scores."""
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    source: str = Field(..., description="The agent or node that generated this confidence score")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Missing info, ambiguities, or reasons for low confidence")
    reasoning: str = Field(..., description="Explanation for the confidence score")
    requires_followup: bool = Field(default=False, description="Flag indicating if the agent needs clarification from user")
    requires_human: bool = Field(default=False, description="Flag indicating if the agent requests human escalation")

class SharedState(TypedDict):
    """Global state shared across all agents in the LangGraph workflow."""
    
    session_id: str
    turn_count: int
    
    # Messages use operator.add to append rather than overwrite in LangGraph
    messages: Annotated[list, operator.add]
    
    patient_info: Dict[str, Any]
    symptoms: List[str]
    extracted_symptoms: Dict[str, Any]
    possible_conditions: List[str]
    analysis: Dict[str, Any]
    
    # Confidence per agent
    confidence_scores: Dict[str, ConfidenceSchema]
    
    escalation_decision: bool
    next_step: str
