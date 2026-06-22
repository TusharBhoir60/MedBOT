"""
Confidence Aggregation Node.
Sprint 3: Weighted aggregation replacing the previous pure-product formula.

Computes a final confidence using configurable weights:
    final = w_symptom * symptom + w_risk * risk + w_retrieval * retrieval + w_diagnosis * diagnosis

If a component is missing (agent hasn't run yet), it is excluded and the
remaining weights are renormalised.
"""
import logging
from typing import Any, Dict

from ai_engine.state import ConfidenceSchema, SharedState
from core.config import settings

logger = logging.getLogger(__name__)


async def aggregate_confidence(state: SharedState) -> Dict[str, Any]:
    """
    Weighted confidence aggregation across CMAR components.
    """
    logger.info("Aggregating confidence scores (weighted)")
    scores = state.get("confidence_scores", {})

    # Map config weight keys to the confidence_scores dict keys
    component_map = {
        "symptom_analysis": settings.ai.weight_symptom,
        "intake": settings.ai.weight_risk,          # intake covers risk/demographics
        "retrieval": settings.ai.weight_retrieval,   # set by DiagnosisAgent
        "diagnosis": settings.ai.weight_diagnosis,   # set by DiagnosisAgent
    }

    weighted_sum = 0.0
    total_weight = 0.0
    uncertainty_factors: list[str] = []

    for key, weight in component_map.items():
        conf = scores.get(key)
        if conf is not None:
            weighted_sum += weight * conf.score
            total_weight += weight
            uncertainty_factors.extend(conf.uncertainty_factors)

    # Renormalise if some components are missing
    combined_val = (weighted_sum / total_weight) if total_weight > 0 else 0.0
    combined_val = min(max(combined_val, 0.0), 1.0)

    # Remove duplicate uncertainty factors while preserving order
    unique_factors = list(dict.fromkeys(uncertainty_factors))

    # Build reasoning string showing components
    parts = []
    for key, weight in component_map.items():
        conf = scores.get(key)
        if conf:
            parts.append(f"{key}={conf.score:.2f}×{weight:.2f}")
    reasoning = "Weighted: " + " + ".join(parts) + f" = {combined_val:.3f}"

    combined = ConfidenceSchema(
        score=round(combined_val, 4),
        source="confidence_aggregator",
        uncertainty_factors=unique_factors,
        reasoning=reasoning,
        requires_followup=bool(unique_factors) or combined_val < settings.ai.confidence_high,
        requires_human=combined_val < settings.ai.confidence_low,
    )

    scores["combined"] = combined
    return {"confidence_scores": scores}
