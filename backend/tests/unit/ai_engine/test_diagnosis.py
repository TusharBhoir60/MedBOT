"""
Comprehensive test suite for the DiagnosisAgent, RAG layer, and
confidence aggregation — Sprint 3.

Covers:
  - Retrieval: exact, partial, synonym, no-match
  - Diagnosis: single disease, overlapping, contradictory, low confidence
  - Confidence: weighted aggregation, propagation, retrieval confidence
  - Citations: attached, dedup, ordering
  - Failures: empty KB, store unavailable, malformed document
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ai_engine.state import ConfidenceSchema, MedicalDocument, SharedState
from ai_engine.agents.diagnosis_agent import (
    DiagnosisAgent,
    DiagnosisOutput,
    LLMDiagnosisExtraction,
)
from ai_engine.rag.vector_store import (
    ChromaVectorStore,
    parse_medical_markdown,
)
from ai_engine.nodes.confidence_aggregator import aggregate_confidence


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_documents():
    return [
        MedicalDocument(
            id="dengue", title="Dengue Fever", source="WHO Dengue Guideline",
            category="infectious", content="Symptoms: high fever, headache, retro-orbital pain, joint pain, rash."
        ),
        MedicalDocument(
            id="malaria", title="Malaria", source="WHO Malaria Guideline",
            category="infectious", content="Symptoms: cyclical fever, chills, rigors, sweating, anaemia."
        ),
        MedicalDocument(
            id="hypertension", title="Hypertension", source="ACC/AHA Guideline",
            category="chronic", content="Symptoms: headache, dizziness, chest pain, visual disturbances."
        ),
        MedicalDocument(
            id="anemia", title="Anemia", source="NICE Anaemia Guideline",
            category="chronic", content="Symptoms: fatigue, pallor, shortness of breath, tachycardia."
        ),
        MedicalDocument(
            id="emergency_red_flags", title="Emergency Red Flags",
            source="Emergency Triage Guideline", category="emergency",
            content="Red flags: chest pain, altered consciousness, severe bleeding, seizures."
        ),
    ]


@pytest.fixture
def mock_vector_store(sample_documents):
    store = MagicMock(spec=ChromaVectorStore)
    store.is_available.return_value = True
    store.document_count.return_value = len(sample_documents)

    def mock_retrieve(query, top_k=5):
        results = []
        query_lower = query.lower()
        for doc in sample_documents:
            score = 0.0
            if doc.title.lower() in query_lower or any(
                w in query_lower for w in doc.content.lower().split(", ")
            ):
                score = 0.9
            elif any(w in query_lower for w in doc.content.lower().split()):
                score = 0.6
            if score > 0:
                results.append((doc, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    store.retrieve.side_effect = mock_retrieve
    return store


@pytest.fixture
def mock_llm_extraction():
    return LLMDiagnosisExtraction(
        primary_diagnosis="Dengue Fever",
        differential_diagnoses=["Malaria", "Chikungunya"],
        urgency_level="urgent",
        reasoning="High fever with retro-orbital pain and rash in tropical region.",
        diagnosis_confidence=0.85,
    )


# ═══════════════════════════════════════════════════════════════════════════
# RETRIEVAL TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestRetrieval:
    def test_exact_match(self, mock_vector_store):
        results = mock_vector_store.retrieve("dengue fever")
        assert len(results) > 0
        assert results[0][0].title == "Dengue Fever"

    def test_partial_match(self, mock_vector_store):
        results = mock_vector_store.retrieve("headache dizziness")
        assert len(results) > 0
        titles = [doc.title for doc, _ in results]
        assert "Hypertension" in titles

    def test_synonym_match(self, mock_vector_store):
        """Synonym matching via content overlap."""
        results = mock_vector_store.retrieve("pallor fatigue")
        assert len(results) > 0
        titles = [doc.title for doc, _ in results]
        assert "Anemia" in titles

    def test_no_match(self, mock_vector_store):
        results = mock_vector_store.retrieve("xyznonexistent123")
        assert len(results) == 0

    def test_retrieval_confidence_calculation(self, mock_vector_store):
        results = mock_vector_store.retrieve("dengue fever")
        scores = [s for _, s in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        assert 0.0 <= avg_score <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSIS TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestDiagnosis:
    @pytest.mark.asyncio
    async def test_single_disease_diagnosis(self, mock_vector_store, mock_llm_extraction):
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=mock_llm_extraction)

        state: dict = {
            "session_id": "t1", "turn_count": 0, "messages": [],
            "patient_info": {"age": 25}, "symptoms": ["fever"],
            "extracted_symptoms": {"symptoms": ["high fever", "rash"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["primary_diagnosis"] == "Dengue Fever"
        assert "Malaria" in result["diagnosis_output"]["differential_diagnoses"]

    @pytest.mark.asyncio
    async def test_overlapping_diseases(self, mock_vector_store):
        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Malaria",
            differential_diagnoses=["Dengue Fever", "Typhoid"],
            urgency_level="urgent",
            reasoning="Cyclical fever with chills; dengue also possible.",
            diagnosis_confidence=0.70,
        )
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "t2", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["cyclical fever", "headache", "rash"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["primary_diagnosis"] == "Malaria"
        assert len(result["diagnosis_output"]["differential_diagnoses"]) >= 1

    @pytest.mark.asyncio
    async def test_contradictory_symptoms(self, mock_vector_store):
        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Unknown",
            differential_diagnoses=["Dengue", "Anemia"],
            urgency_level="routine",
            reasoning="Contradictory: fever + pallor + joint pain are inconsistent.",
            diagnosis_confidence=0.35,
        )
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "t3", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["fever", "pallor", "joint pain"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["diagnosis_confidence"] < 0.5

    @pytest.mark.asyncio
    async def test_low_confidence_flags_followup(self, mock_vector_store):
        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Possible Dengue",
            differential_diagnoses=[],
            urgency_level="routine",
            reasoning="Insufficient data.",
            diagnosis_confidence=0.4,
        )
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "t4", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["mild fever"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        diag_conf = result["confidence_scores"]["diagnosis"]
        assert diag_conf.requires_followup is True

    @pytest.mark.asyncio
    async def test_emergency_urgency_flags_human(self, mock_vector_store):
        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Severe Dengue",
            differential_diagnoses=["Dengue Shock Syndrome"],
            urgency_level="emergency",
            reasoning="Severe bleeding, altered consciousness.",
            diagnosis_confidence=0.92,
        )
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "t5", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["severe bleeding"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["confidence_scores"]["diagnosis"].requires_human is True


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE AGGREGATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestConfidenceAggregation:
    @pytest.mark.asyncio
    async def test_weighted_aggregation_all_components(self):
        state: dict = {
            "confidence_scores": {
                "intake": ConfidenceSchema(score=0.90, source="intake", reasoning="OK"),
                "symptom_analysis": ConfidenceSchema(score=0.85, source="symptom", reasoning="OK"),
                "retrieval": ConfidenceSchema(score=0.80, source="retrieval", reasoning="OK"),
                "diagnosis": ConfidenceSchema(score=0.75, source="diagnosis", reasoning="OK"),
            }
        }
        result = await aggregate_confidence(state)
        combined = result["confidence_scores"]["combined"]
        # 0.30*0.85 + 0.20*0.90 + 0.25*0.80 + 0.25*0.75 = 0.255+0.18+0.20+0.1875 = 0.8225
        assert 0.80 <= combined.score <= 0.85

    @pytest.mark.asyncio
    async def test_weighted_aggregation_missing_components(self):
        state: dict = {
            "confidence_scores": {
                "intake": ConfidenceSchema(score=0.90, source="intake", reasoning="OK"),
                "symptom_analysis": ConfidenceSchema(score=0.80, source="symptom", reasoning="OK"),
            }
        }
        result = await aggregate_confidence(state)
        combined = result["confidence_scores"]["combined"]
        # Only intake(0.20 weight) + symptom(0.30 weight) present
        # renormalised: (0.20*0.90 + 0.30*0.80) / 0.50 = (0.18+0.24)/0.50 = 0.84
        assert 0.80 <= combined.score <= 0.90

    @pytest.mark.asyncio
    async def test_confidence_propagation_with_diagnosis(self):
        state: dict = {
            "confidence_scores": {
                "intake": ConfidenceSchema(score=0.95, source="intake", reasoning="OK"),
                "symptom_analysis": ConfidenceSchema(score=0.90, source="symptom", reasoning="OK"),
                "retrieval": ConfidenceSchema(score=0.70, source="retrieval", reasoning="OK"),
                "diagnosis": ConfidenceSchema(score=0.60, source="diagnosis", reasoning="Low"),
            }
        }
        result = await aggregate_confidence(state)
        combined = result["confidence_scores"]["combined"]
        assert combined.score < 0.85  # low diagnosis drags it down

    @pytest.mark.asyncio
    async def test_retrieval_confidence_calculation(self):
        state: dict = {
            "confidence_scores": {
                "retrieval": ConfidenceSchema(
                    score=0.3, source="retrieval", reasoning="Poor match",
                    uncertainty_factors=["Low retrieval relevance"],
                ),
            }
        }
        result = await aggregate_confidence(state)
        combined = result["confidence_scores"]["combined"]
        assert "Low retrieval relevance" in combined.uncertainty_factors

    @pytest.mark.asyncio
    async def test_empty_scores(self):
        state: dict = {"confidence_scores": {}}
        result = await aggregate_confidence(state)
        combined = result["confidence_scores"]["combined"]
        assert combined.score == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# CITATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCitations:
    @pytest.mark.asyncio
    async def test_citations_attached(self, mock_vector_store, mock_llm_extraction):
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=mock_llm_extraction)

        state: dict = {
            "session_id": "c1", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["fever", "headache"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert isinstance(result["citations"], list)
        assert len(result["citations"]) > 0
        assert "WHO Dengue Guideline" in result["citations"]

    @pytest.mark.asyncio
    async def test_citation_deduplication(self, mock_vector_store, mock_llm_extraction):
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=mock_llm_extraction)

        state: dict = {
            "session_id": "c2", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["fever"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        citations = result["citations"]
        assert len(citations) > 0
        assert len(citations) == len(set(citations))  # no duplicates

    @pytest.mark.asyncio
    async def test_citation_ordering(self, mock_vector_store, mock_llm_extraction):
        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = mock_vector_store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=mock_llm_extraction)

        state: dict = {
            "session_id": "c3", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["dengue fever", "cyclical fever"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        citations = result["citations"]
        assert len(citations) >= 2
        # Dengue Fever has title match (0.9), cyclical fever matches Malaria content (0.6)
        assert citations[0] == "WHO Dengue Guideline"
        assert citations[1] == "WHO Malaria Guideline"


# ═══════════════════════════════════════════════════════════════════════════
# FAILURE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestFailures:
    @pytest.mark.asyncio
    async def test_empty_kb(self):
        store = MagicMock(spec=ChromaVectorStore)
        store.is_available.return_value = True
        store.retrieve.return_value = []
        store.document_count.return_value = 0

        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Unknown",
            differential_diagnoses=[],
            urgency_level="routine",
            reasoning="No KB evidence available.",
            diagnosis_confidence=0.3,
        )

        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "f1", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["cough"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["retrieval_confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_vector_store_unavailable(self):
        store = MagicMock(spec=ChromaVectorStore)
        store.is_available.return_value = False

        extraction = LLMDiagnosisExtraction(
            primary_diagnosis="Unknown",
            differential_diagnoses=[],
            urgency_level="routine",
            reasoning="Vector store unavailable.",
            diagnosis_confidence=0.2,
        )

        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(return_value=extraction)

        state: dict = {
            "session_id": "f2", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["chest pain"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["retrieval_confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_llm_failure_graceful_degradation(self):
        store = MagicMock(spec=ChromaVectorStore)
        store.is_available.return_value = True
        store.retrieve.return_value = []

        agent = DiagnosisAgent.__new__(DiagnosisAgent)
        agent.vector_store = store
        agent.llm = MagicMock()
        agent.structured_llm = MagicMock()
        agent.structured_llm.ainvoke = AsyncMock(side_effect=Exception("LLM timeout"))

        state: dict = {
            "session_id": "f3", "turn_count": 0, "messages": [],
            "patient_info": {}, "symptoms": [],
            "extracted_symptoms": {"symptoms": ["unknown"]},
            "possible_conditions": [], "analysis": {},
            "confidence_scores": {}, "diagnosis_output": {},
            "citations": [], "escalation_decision": False, "next_step": "diagnosis",
        }

        result = await agent.invoke(state)
        assert result["diagnosis_output"]["primary_diagnosis"] == "Unknown"
        assert result["confidence_scores"]["diagnosis"].score == 0.0

    def test_malformed_document_parse(self, tmp_path):
        malformed = tmp_path / "bad.md"
        malformed.write_text("This file has no headings at all.", encoding="utf-8")
        doc = parse_medical_markdown(malformed)
        assert doc.title == "Bad"
        assert doc.content == "This file has no headings at all."


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSchemas:
    def test_diagnosis_output_schema(self):
        output = DiagnosisOutput(
            primary_diagnosis="Dengue",
            differential_diagnoses=["Malaria"],
            urgency_level="urgent",
            reasoning="Clear symptoms.",
            citations=["WHO Guideline"],
            retrieval_confidence=0.9,
            diagnosis_confidence=0.85,
        )
        assert output.primary_diagnosis == "Dengue"
        assert output.retrieval_confidence == 0.9

    def test_medical_document_schema(self):
        doc = MedicalDocument(
            id="test", title="Test", source="Test Source",
            category="general", content="Test content",
        )
        assert doc.version is None

    def test_confidence_schema_bounds(self):
        with pytest.raises(Exception):
            ConfidenceSchema(score=1.5, source="test", reasoning="Invalid")
