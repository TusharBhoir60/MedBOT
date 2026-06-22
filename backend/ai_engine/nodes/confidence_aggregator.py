"""
Confidence Aggregation Node.
Combines confidence scores from upstream agents.
"""
import logging
from typing import Dict, Any

from ai_engine.state import SharedState, ConfidenceSchema

logger = logging.getLogger(__name__)

async def aggregate_confidence(state: SharedState) -> Dict[str, Any]:
    """
    Collects confidence from agents and calculates a combined score using the product approach.
    """
    logger.info("Aggregating confidence scores")
    scores = state.get("confidence_scores", {})
    
    intake_conf = scores.get("intake")
    symptom_conf = scores.get("symptom_analysis")
    
    # If missing, we treat as 1.0 so it doesn't artificially drag down the product
    # if an agent wasn't meant to run. If neither ran, it remains 1.0.
    intake_val = intake_conf.score if intake_conf else 1.0
    symptom_val = symptom_conf.score if symptom_conf else 1.0
    
    combined_val = intake_val * symptom_val
    
    uncertainty_factors = []
    if intake_conf:
        uncertainty_factors.extend(intake_conf.uncertainty_factors)
    if symptom_conf:
        uncertainty_factors.extend(symptom_conf.uncertainty_factors)
        
    # Remove duplicates while preserving order
    unique_factors = list(dict.fromkeys(uncertainty_factors))
    
    combined = ConfidenceSchema(
        score=combined_val,
        source="confidence_aggregator",
        uncertainty_factors=unique_factors,
        reasoning=f"Product of intake ({intake_val:.2f}) and symptom ({symptom_val:.2f})",
        requires_followup=bool(unique_factors) or combined_val < 0.85, 
        requires_human=combined_val < 0.50
    )
    
    scores["combined"] = combined
    return {"confidence_scores": scores}
