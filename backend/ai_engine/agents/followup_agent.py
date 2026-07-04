"""
Follow-up Agent implementation.
Responsible for formulating questions to resolve uncertainty factors.
"""
import logging
from typing import Any, Dict

from langchain_core.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field
from core.config import settings
from ai_engine.providers import get_llm_provider

from ai_engine.interfaces import AgentInterface
from ai_engine.state import SharedState
from ai_engine.prompts.registry import FOLLOWUP_PROMPT

logger = logging.getLogger(__name__)

class FollowupOutput(BaseModel):
    question: str = Field(..., description="The follow-up question to ask the user")

class FollowUpAgent(AgentInterface):
    """Generates a clarification question based on uncertainty factors."""
    
    def __init__(self, llm: Optional[BaseChatModel] = None) -> None:
        self.llm = llm or get_llm_provider(model_name=settings.ai.model_primary, temperature=0.7)
        self.structured_llm = self.llm.with_structured_output(FollowupOutput)
        
    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        logger.info("FollowUpAgent invoked")
        
        # Aggregate uncertainty factors
        scores = state.get("confidence_scores", {})
        combined = scores.get("combined")
        uncertainty_factors = combined.uncertainty_factors if combined else []
        
        if not uncertainty_factors:
            logger.warning("FollowUpAgent called but no uncertainty factors found.")
            return {"turn_count": state.get("turn_count", 0) + 1}
            
        prompt = FOLLOWUP_PROMPT.format(uncertainty_factors=uncertainty_factors)
        
        try:
            # Type ignore because with_structured_output typing is complex
            output: FollowupOutput = await self.structured_llm.ainvoke(prompt)  # type: ignore
            
            new_message = AIMessage(content=output.question)
            
            return {
                "messages": [new_message],
                "turn_count": state.get("turn_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"Error in FollowUpAgent: {e}")
            fallback_msg = AIMessage(content="Could you please provide more details about your symptoms?")
            return {
                "messages": [fallback_msg],
                "turn_count": state.get("turn_count", 0) + 1
            }
