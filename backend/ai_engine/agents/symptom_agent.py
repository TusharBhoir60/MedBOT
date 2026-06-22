"""
Symptom Analysis Agent implementation.
Responsible for normalizing symptoms and suggesting possible conditions based on clinical context.
"""
import logging
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ai_engine.interfaces import AgentInterface
from ai_engine.state import ConfidenceSchema, SharedState

logger = logging.getLogger(__name__)

class AnalysisExtraction(BaseModel):
    """Schema for LLM to extract structured symptoms and possible conditions."""
    extracted_symptoms: list[str] = Field(..., description="Standardized medical terms for the raw symptoms")
    possible_conditions: list[str] = Field(..., description="List of possible medical conditions")
    analysis: str = Field(..., description="Detailed medical analysis and triage recommendation")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis and triage")
    uncertainty_factors: list[str] = Field(default_factory=list, description="Ambiguous symptoms or missing clinical data")
    confidence_reasoning: str = Field(..., description="Reasoning for the confidence score")
    requires_followup: bool = Field(default=False, description="True if missing clinical context prevents accurate triage")


class SymptomAgent(AgentInterface):
    """Agent that analyzes symptoms and patient info to provide possible conditions."""
    
    def __init__(self, llm: ChatOpenAI | None = None) -> None:
        # Defaults to gpt-4o for clinical reasoning
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(AnalysisExtraction)
        
    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        logger.info("SymptomAgent invoked")
        
        patient_info = state.get("patient_info", {})
        raw_symptoms = state.get("symptoms", [])
        
        if not raw_symptoms:
            logger.warning("No symptoms provided to SymptomAgent.")
            return {"next_step": "end"}
            
        prompt = f"""
        You are a highly capable clinical triage assistant.
        Analyze the following patient profile and symptoms to provide a standardized list of symptoms, possible conditions, and a detailed analysis.
        
        Patient Profile:
        {patient_info}
        
        Raw Symptoms:
        {raw_symptoms}
        
        Provide the output in the requested structured format.
        """
        
        try:
            # Type ignore because with_structured_output typing is complex
            extraction: AnalysisExtraction = await self.structured_llm.ainvoke(prompt) # type: ignore
            
            confidence = ConfidenceSchema(
                score=extraction.confidence_score,
                source="symptom_analysis",
                uncertainty_factors=extraction.uncertainty_factors,
                reasoning=extraction.confidence_reasoning,
                requires_followup=extraction.requires_followup,
                requires_human=extraction.confidence_score < 0.5
            )
            
            confidence_scores = state.get("confidence_scores", {})
            confidence_scores["symptom_analysis"] = confidence
            
            return {
                "extracted_symptoms": extraction.extracted_symptoms,
                "possible_conditions": extraction.possible_conditions,
                "analysis": extraction.analysis,
                "confidence_scores": confidence_scores
            }
            
        except Exception as e:
            logger.error(f"Error in SymptomAgent: {e}")
            confidence = ConfidenceSchema(
                score=0.0,
                source="symptom_analysis",
                uncertainty_factors=[f"Analysis failed: {str(e)}"],
                reasoning="Agent exception occurred",
                requires_followup=True,
                requires_human=True
            )
            confidence_scores = state.get("confidence_scores", {})
            confidence_scores["symptom_analysis"] = confidence
            
            return {
                "confidence_scores": confidence_scores
            }
