"""
Integration tests for the Chat invoke endpoint.
Verifies session creation, message routing, session store persistence,
and schema serialization matching specifications.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from ai_engine.state import ConfidenceSchema

@pytest.mark.asyncio
async def test_chat_invoke_workflow_integration(client: AsyncClient):
    """Test that /chat/invoke successfully routes to the CMAR workflow and handles sessions."""
    
    # Patch the invoke methods of the agents directly to avoid external LLM/DB calls
    with patch("ai_engine.agents.intake_agent.IntakeAgent.invoke", new_callable=AsyncMock) as mock_intake, \
         patch("ai_engine.agents.symptom_agent.SymptomAgent.invoke", new_callable=AsyncMock) as mock_symptom, \
         patch("ai_engine.agents.diagnosis_agent.DiagnosisAgent.invoke", new_callable=AsyncMock) as mock_diagnosis:

        async def intake_side_effect(state):
            scores = state.get("confidence_scores", {})
            scores["intake"] = ConfidenceSchema(
                score=0.95,
                source="intake",
                reasoning="High quality intake message",
                requires_followup=False,
                requires_human=False
            )
            return {"confidence_scores": scores}
        mock_intake.side_effect = intake_side_effect

        async def symptom_side_effect(state):
            scores = state.get("confidence_scores", {})
            scores["symptom_analysis"] = ConfidenceSchema(
                score=0.90,
                source="symptom_analysis",
                reasoning="Clear symptoms matched",
                requires_followup=False,
                requires_human=False
            )
            return {
                "extracted_symptoms": ["fever", "rash"],
                "possible_conditions": ["Dengue Fever"],
                "analysis": {"summary": "High fever, retro-orbital pain, likely Dengue."},
                "confidence_scores": scores
            }
        mock_symptom.side_effect = symptom_side_effect

        async def diagnosis_side_effect(state):
            scores = state.get("confidence_scores", {})
            scores["retrieval"] = ConfidenceSchema(
                score=0.85,
                source="retrieval",
                reasoning="Retrieval results relevant",
                requires_followup=False,
                requires_human=False
            )
            scores["diagnosis"] = ConfidenceSchema(
                score=0.90,
                source="diagnosis",
                reasoning="Clinical reasoning aligns",
                requires_followup=False,
                requires_human=False
            )
            return {
                "diagnosis_output": {
                    "primary_diagnosis": "Dengue Fever",
                    "differential_diagnoses": ["Malaria"],
                    "urgency_level": "urgent",
                    "reasoning": "Fever and rash in tropical area.",
                    "citations": ["WHO Dengue Guideline"],
                    "retrieval_confidence": 0.85,
                    "diagnosis_confidence": 0.90,
                },
                "possible_conditions": ["Dengue Fever", "Malaria"],
                "citations": ["WHO Dengue Guideline"],
                "confidence_scores": scores
            }
        mock_diagnosis.side_effect = diagnosis_side_effect

        # Payload for new session
        payload = {
            "session_id": "test-session-int-1",
            "message": "I have high fever and rash",
            "patient_info": {"age": 30, "gender": "female"},
            "symptoms": ["fever"]
        }

        # First request (New Session)
        response = await client.post("/api/v1/chat/invoke", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-int-1"
        assert "messages" in data
        assert len(data["messages"]) > 0
        assert data["diagnosis_output"]["primary_diagnosis"] == "Dengue Fever"
        assert data["confidence_scores"]["combined"]["score"] > 0.8
        
        # Verify mock calls
        mock_intake.assert_called_once()
        mock_symptom.assert_called_once()
        mock_diagnosis.assert_called_once()

        # Second request (Existing Session to test persistence)
        mock_intake.reset_mock()
        mock_symptom.reset_mock()
        mock_diagnosis.reset_mock()

        followup_payload = {
            "session_id": "test-session-int-1",
            "message": "It started 3 days ago",
            "patient_info": {"location": "Mumbai"},
            "symptoms": ["rash"]
        }

        response2 = await client.post("/api/v1/chat/invoke", json=followup_payload)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == "test-session-int-1"
        # Messages should contain both messages
        assert len(data2["messages"]) >= 2
        # Verify updated info persisted
        assert data2["patient_info"]["location"] == "Mumbai"
        assert "rash" in data2["symptoms"]
