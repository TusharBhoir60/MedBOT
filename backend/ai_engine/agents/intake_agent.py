"""
Intake Agent implementation.
Responsible for extracting initial patient demographics and raw symptoms.
"""
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from core.config import settings
from ai_engine.providers import get_llm_provider
from pydantic import BaseModel, Field

from ai_engine.interfaces import AgentInterface
from ai_engine.state import ConfidenceSchema, SharedState
from ai_engine.prompts.registry import INTAKE_PROMPT

logger = logging.getLogger(__name__)

class IntakeExtraction(BaseModel):
    """Schema for LLM to extract intake information."""
    age: int | None = Field(default=None, description="Patient's age if mentioned")
    gender: str | None = Field(default=None, description="Patient's gender if mentioned")
    pre_existing_conditions: list[str] = Field(default_factory=list, description="Any pre-existing medical conditions mentioned")
    symptoms: list[str] = Field(default_factory=list, description="List of raw symptoms mentioned by the patient")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the extraction")
    uncertainty_factors: list[str] = Field(default_factory=list, description="Missing demographic info or ambiguity")
    confidence_reasoning: str = Field(..., description="Reasoning for the confidence score")
    requires_followup: bool = Field(default=False, description="True if missing info prevents a complete profile")


class IntakeAgent(AgentInterface):
    """Agent that extracts initial demographic and symptom data from the user's message."""
    
    def __init__(self, llm: BaseChatModel | None = None) -> None:
        # Defaults to model_fast for structured extraction
        self.llm = llm or get_llm_provider(model_name=settings.ai.model_fast, temperature=0.0)
        self.structured_llm = self.llm.with_structured_output(IntakeExtraction)
        
    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        logger.info("IntakeAgent invoked")
        
        messages = state.get("messages", [])
        if not messages:
            logger.warning("No messages found in state.")
            return {}
            
        # Get the latest message content
        latest_message = messages[-1]
        content = latest_message.content if hasattr(latest_message, "content") else str(latest_message)
        
        prompt = INTAKE_PROMPT.format(content=content)
        
        try:
            # Type ignore because with_structured_output typing is complex
            extraction: IntakeExtraction = await self.structured_llm.ainvoke(prompt)  # type: ignore
            
            patient_info = state.get("patient_info", {})
            if extraction.age:
                patient_info["age"] = extraction.age
            if extraction.gender:
                patient_info["gender"] = extraction.gender
            if extraction.pre_existing_conditions:
                patient_info["pre_existing_conditions"] = extraction.pre_existing_conditions
                
            confidence = ConfidenceSchema(
                score=extraction.confidence_score,
                source="intake",
                uncertainty_factors=extraction.uncertainty_factors,
                reasoning=extraction.confidence_reasoning,
                requires_followup=extraction.requires_followup,
                requires_human=extraction.confidence_score < 0.5
            )
            
            confidence_scores = state.get("confidence_scores", {})
            confidence_scores["intake"] = confidence
            
            return {
                "patient_info": patient_info,
                "symptoms": extraction.symptoms,
                "confidence_scores": confidence_scores
            }
            
        except Exception as e:
            logger.error(f"Error in IntakeAgent: {e}")
            confidence = ConfidenceSchema(
                score=0.0,
                source="intake",
                uncertainty_factors=[f"Extraction failed: {str(e)}"],
                reasoning="Agent exception occurred",
                requires_followup=True,
                requires_human=True
            )
            confidence_scores = state.get("confidence_scores", {})
            confidence_scores["intake"] = confidence
            
            return {
                "confidence_scores": confidence_scores
            }
