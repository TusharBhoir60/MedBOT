"""
Diagnosis Agent Stub.
Responsible for formal medical diagnosis outputs.
"""
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field

from ai_engine.interfaces import AgentInterface
from ai_engine.state import ConfidenceSchema, SharedState

logger = logging.getLogger(__name__)

class DiagnosisOutput(BaseModel):
    possible_conditions: list[str] = Field(..., description="List of possible conditions")
    differential_diagnoses: list[str] = Field(..., description="Alternative diagnoses to consider")
    urgency_level: str = Field(..., description="e.g. routine, urgent, emergency")
    confidence: ConfidenceSchema = Field(..., description="Confidence of the diagnosis")

class DiagnosisAgent(AgentInterface):
    """Stub agent for generating final diagnoses (Sprint 3 target)."""
    
    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        logger.info("DiagnosisAgent invoked (STUB)")
        
        # Stub implementation
        confidence = ConfidenceSchema(
            score=0.9,
            source="diagnosis",
            uncertainty_factors=[],
            reasoning="Stub implementation",
            requires_followup=False,
            requires_human=False
        )
        
        diagnosis = DiagnosisOutput(
            possible_conditions=state.get("possible_conditions", ["Unknown"]),
            differential_diagnoses=[],
            urgency_level="routine",
            confidence=confidence
        )
        
        return {
            "possible_conditions": diagnosis.possible_conditions
            # In a full implementation, we'd store the full DiagnosisOutput somewhere in state
        }
