"""
Diagnosis Agent — RAG-powered differential diagnosis.

Retrieves evidence from the Medical Knowledge Base via the vector store,
then uses an LLM to produce structured differential diagnoses with
citations and per-component confidence scores.
"""
import logging
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field
from core.config import settings
from ai_engine.providers import get_llm_provider

from ai_engine.interfaces import AgentInterface
from ai_engine.rag.vector_store import get_vector_store
from ai_engine.state import ConfidenceSchema, SharedState
from ai_engine.prompts.registry import DIAGNOSIS_PROMPT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class DiagnosisOutput(BaseModel):
    """Formal output contract for the Diagnosis Agent."""
    primary_diagnosis: str = Field(..., description="Most likely diagnosis")
    differential_diagnoses: List[str] = Field(
        ..., description="Alternative diagnoses to consider"
    )
    urgency_level: str = Field(
        ..., description="Triage urgency: routine, urgent, or emergency"
    )
    reasoning: str = Field(..., description="Clinical reasoning chain")
    citations: List[str] = Field(
        default_factory=list,
        description="Deduplicated source citations ordered by relevance",
    )
    retrieval_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence derived from retrieval quality"
    )
    diagnosis_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="LLM's self-assessed diagnosis confidence"
    )


class LLMDiagnosisExtraction(BaseModel):
    """Schema for the LLM structured output call."""
    primary_diagnosis: str = Field(..., description="Most likely diagnosis")
    differential_diagnoses: List[str] = Field(
        ..., description="Alternative diagnoses"
    )
    urgency_level: str = Field(
        ..., description="One of: routine, urgent, emergency"
    )
    reasoning: str = Field(..., description="Step-by-step clinical reasoning")
    diagnosis_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Self-assessed confidence in the diagnosis",
    )


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class DiagnosisAgent(AgentInterface):
    """RAG-powered agent that produces differential diagnoses with citations."""

    def __init__(self, llm: Optional[BaseChatModel] = None) -> None:
        self.llm = llm or get_llm_provider(model_name=settings.ai.model_primary, temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(LLMDiagnosisExtraction)
        self.vector_store = get_vector_store()

    # -- public interface ---------------------------------------------------

    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        logger.info("DiagnosisAgent invoked")

        extracted_symptoms = state.get("extracted_symptoms", {})
        patient_info = state.get("patient_info", {})
        possible_conditions = state.get("possible_conditions", [])

        # Step 1 — build retrieval query
        query = self._build_query(extracted_symptoms, patient_info, possible_conditions)

        # Step 2 — retrieve evidence
        retrieved_results, retrieval_confidence = self._retrieve_evidence(query)
        context = self._format_context(retrieved_results)

        # Step 3 — generate diagnosis
        # Build retrieval confidence
        retrieval_conf = ConfidenceSchema(
            score=retrieval_confidence,
            source="retrieval",
            uncertainty_factors=(
                ["No medical documents retrieved"] if retrieval_confidence == 0.0 else []
            ),
            reasoning=f"Average similarity score of retrieved documents: {retrieval_confidence:.2f}",
            requires_followup=retrieval_confidence < settings.ai.confidence_medium,
            requires_human=retrieval_confidence < settings.ai.confidence_low,
        )

        confidence_scores = state.get("confidence_scores", {})
        confidence_scores["retrieval"] = retrieval_conf

        try:
            diagnosis = await self._generate_diagnosis(
                query, context, patient_info, extracted_symptoms
            )
        except Exception as exc:
            logger.error("DiagnosisAgent LLM call failed: %s", exc)
            return self._fallback_result(str(exc), confidence_scores)

        # Step 4 — assemble citations (deduplicated, ordered by relevance)
        citations = self._assemble_citations(retrieved_results)

        # Build confidence
        confidence = ConfidenceSchema(
            score=diagnosis.diagnosis_confidence,
            source="diagnosis",
            uncertainty_factors=(
                ["Low retrieval relevance"] if retrieval_confidence < 0.5 else []
            ),
            reasoning=diagnosis.reasoning,
            requires_followup=diagnosis.diagnosis_confidence < settings.ai.diagnosis_followup_threshold,
            requires_human=diagnosis.urgency_level == settings.ai.emergency_urgency_trigger,
        )

        confidence_scores["diagnosis"] = confidence

        diagnosis_output = DiagnosisOutput(
            primary_diagnosis=diagnosis.primary_diagnosis,
            differential_diagnoses=diagnosis.differential_diagnoses,
            urgency_level=diagnosis.urgency_level,
            reasoning=diagnosis.reasoning,
            citations=citations,
            retrieval_confidence=retrieval_confidence,
            diagnosis_confidence=diagnosis.diagnosis_confidence,
        )

        return {
            "diagnosis_output": diagnosis_output.model_dump(),
            "possible_conditions": [diagnosis.primary_diagnosis]
            + diagnosis.differential_diagnoses,
            "citations": citations,
            "confidence_scores": confidence_scores,
        }

    # -- private helpers ----------------------------------------------------

    def _build_query(
        self,
        extracted_symptoms: Dict[str, Any],
        patient_info: Dict[str, Any],
        possible_conditions: List[str],
    ) -> str:
        """Combine symptoms, demographics, and prior conditions into a retrieval query."""
        parts: List[str] = []

        # Flatten extracted symptoms
        if isinstance(extracted_symptoms, dict):
            symptoms_list = extracted_symptoms.get("symptoms", list(extracted_symptoms.keys()))
        else:
            symptoms_list = list(extracted_symptoms) if extracted_symptoms else []
        if symptoms_list:
            parts.append("Symptoms: " + ", ".join(str(s) for s in symptoms_list))

        # Demographics
        age = patient_info.get("age")
        gender = patient_info.get("gender")
        if age or gender:
            demo = " ".join(filter(None, [str(age) if age else None, gender]))
            parts.append(f"Patient: {demo}")

        if possible_conditions:
            parts.append("Possible conditions: " + ", ".join(possible_conditions))

        return ". ".join(parts) if parts else "general medical symptoms"

    def _retrieve_evidence(
        self, query: str
    ) -> tuple[list, float]:
        """Retrieve from the vector store. Returns (results_list, retrieval_confidence)."""
        if not self.vector_store.is_available():
            logger.warning("Vector store unavailable — degrading gracefully.")
            return [], 0.0

        results = self.vector_store.retrieve(query, top_k=settings.ai.rag_top_k)

        if not results:
            logger.warning("No documents retrieved from the medical KB.")
            return [], 0.0

        scores = [score for _, score in results]
        retrieval_confidence = sum(scores) / len(scores) if scores else 0.0
        return results, min(retrieval_confidence, 1.0)

    def _format_context(self, results: list) -> str:
        """Format retrieval results into a single context string for the LLM prompt."""
        parts = [
            f"--- {doc.title} (Source: {doc.source}) ---\n{doc.content}"
            for doc, _ in results
        ]
        return "\n\n".join(parts)

    async def _generate_diagnosis(
        self,
        query: str,
        context: str,
        patient_info: Dict[str, Any],
        extracted_symptoms: Dict[str, Any],
    ) -> LLMDiagnosisExtraction:
        """Prompt the LLM with retrieved evidence and patient state."""
        context_final = context if context else "No evidence retrieved. Rely on parametric knowledge only."
        prompt = DIAGNOSIS_PROMPT.format(
            patient_info=patient_info,
            extracted_symptoms=extracted_symptoms,
            context=context_final
        )
        
        extraction: LLMDiagnosisExtraction = await self.structured_llm.ainvoke(prompt)  # type: ignore
        return extraction

    def _assemble_citations(self, results: list) -> List[str]:
        """Extract unique, relevance-ordered citation sources from retrieval results."""
        seen: set[str] = set()
        citations: List[str] = []
        for doc, _ in results:  # results already sorted by relevance descending
            if doc.source not in seen:
                seen.add(doc.source)
                citations.append(doc.source)
        return citations

    def _fallback_result(self, error: str, confidence_scores: Dict[str, ConfidenceSchema]) -> Dict[str, Any]:
        """Graceful degradation when the LLM call fails entirely."""
        confidence = ConfidenceSchema(
            score=0.0,
            source="diagnosis",
            uncertainty_factors=[f"Diagnosis generation failed: {error}"],
            reasoning="Agent exception occurred",
            requires_followup=True,
            requires_human=True,
        )
        confidence_scores["diagnosis"] = confidence
        return {
            "diagnosis_output": {
                "primary_diagnosis": "Unknown",
                "differential_diagnoses": [],
                "urgency_level": "urgent",
                "reasoning": f"Diagnosis generation failed: {error}",
                "citations": [],
                "retrieval_confidence": 0.0,
                "diagnosis_confidence": 0.0,
            },
            "possible_conditions": [],
            "citations": [],
            "confidence_scores": confidence_scores,
        }
