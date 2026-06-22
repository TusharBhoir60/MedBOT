"""
Confidence Check Node.
Strictly handles routing based on aggregated confidence and config thresholds.
"""
import logging
from typing import Dict, Any

from ai_engine.state import SharedState
from core.config import settings

logger = logging.getLogger(__name__)

async def evaluate_confidence(state: SharedState) -> Dict[str, Any]:
    """
    Evaluates the combined confidence score and enforces max follow-ups.
    """
    logger.info("Evaluating confidence routing")
    
    turn_count = state.get("turn_count", 0)
    
    # Prevent infinite loops
    if turn_count >= settings.ai.max_followups:
        logger.warning(f"Max followups ({settings.ai.max_followups}) reached. Escalating to human.")
        return {"next_step": "handoff", "escalation_decision": True}
        
    scores = state.get("confidence_scores", {})
    combined = scores.get("combined")
    
    if not combined:
        logger.error("No combined confidence found. Defaulting to handoff.")
        return {"next_step": "handoff", "escalation_decision": True}
        
    if combined.score >= settings.ai.confidence_high:
        return {"next_step": "diagnosis"}
    elif combined.score >= settings.ai.confidence_low:
        return {"next_step": "followup"}
    else:
        return {"next_step": "handoff", "escalation_decision": True}
