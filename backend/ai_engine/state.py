"""
Shared state schemas for the LangGraph AI workflow.
Implements the CMAR (Confidence-Weighted Multi-Agent Reasoning) state.
"""
from typing import Annotated, Any, Dict, List, Optional, TypedDict
import operator
from pydantic import BaseModel, Field

class ConfidenceSchema(BaseModel):
    """Schema for individual agent confidence scores."""
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Explanation for the confidence score")

class SharedState(TypedDict):
    """Global state shared across all agents in the LangGraph workflow."""
    # Messages use operator.add to append rather than overwrite in LangGraph
    messages: Annotated[list, operator.add]
    
    patient_info: Dict[str, Any]
    symptoms: List[str]
    extracted_symptoms: List[str]
    possible_conditions: List[str]
    analysis: str
    
    # Confidence per agent
    confidence_scores: Dict[str, ConfidenceSchema]
    
    escalation_decision: bool
    next_step: str
