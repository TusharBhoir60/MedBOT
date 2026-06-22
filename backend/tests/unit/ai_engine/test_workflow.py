import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from ai_engine.state import SharedState, ConfidenceSchema
from ai_engine.workflow import create_workflow

@pytest.fixture
def mock_agents():
    with patch("ai_engine.workflow.IntakeAgent") as MockIntake, \
         patch("ai_engine.workflow.SymptomAgent") as MockSymptom, \
         patch("ai_engine.workflow.FollowUpAgent") as MockFollowUp, \
         patch("ai_engine.workflow.DiagnosisAgent") as MockDiagnosis:
         
        intake = MockIntake.return_value
        intake.invoke = AsyncMock()
        
        symptom = MockSymptom.return_value
        symptom.invoke = AsyncMock()
        
        followup = MockFollowUp.return_value
        followup.invoke = AsyncMock()
        
        diagnosis = MockDiagnosis.return_value
        diagnosis.invoke = AsyncMock()
        
        yield {
            "intake": intake,
            "symptom": symptom,
            "followup": followup,
            "diagnosis": diagnosis
        }

@pytest.mark.asyncio
async def test_workflow_high_confidence_path(mock_agents):
    """Test the workflow when confidence is high."""
    
    mock_agents["intake"].invoke.return_value = {
        "confidence_scores": {"intake": ConfidenceSchema(score=0.9, source="intake", reasoning="OK", requires_followup=False, requires_human=False)}
    }
    mock_agents["symptom"].invoke.return_value = {
        "confidence_scores": {"symptom_analysis": ConfidenceSchema(score=0.95, source="symptom", reasoning="OK", requires_followup=False, requires_human=False)}
    }
    mock_agents["diagnosis"].invoke.return_value = {
        "possible_conditions": ["Condition A"]
    }
    
    app = create_workflow()
    initial_state = {
        "session_id": "test_1",
        "turn_count": 0,
        "messages": [HumanMessage(content="I have a headache.")],
        "patient_info": {},
        "symptoms": [],
        "extracted_symptoms": {},
        "possible_conditions": [],
        "analysis": {},
        "confidence_scores": {},
        "escalation_decision": False,
        "next_step": "intake"
    }
    
    final_state = await app.ainvoke(initial_state)
    
    # Assertions
    assert "combined" in final_state["confidence_scores"]
    assert final_state["confidence_scores"]["combined"].score == 0.9 * 0.95
    mock_agents["diagnosis"].invoke.assert_called_once()

@pytest.mark.asyncio
async def test_workflow_followup_path(mock_agents):
    """Test the workflow routing to follow-up on medium confidence."""
    
    mock_agents["intake"].invoke.return_value = {
        "confidence_scores": {"intake": ConfidenceSchema(score=0.8, source="intake", reasoning="OK", requires_followup=False, requires_human=False)}
    }
    mock_agents["symptom"].invoke.return_value = {
        "confidence_scores": {"symptom_analysis": ConfidenceSchema(score=0.8, source="symptom", reasoning="OK", requires_followup=True, uncertainty_factors=["Missing info"], requires_human=False)}
    }
    mock_agents["followup"].invoke.return_value = {
        "messages": [AIMessage(content="Could you tell me more?")],
        "turn_count": 1
    }
    
    app = create_workflow()
    initial_state = {
        "session_id": "test_2",
        "turn_count": 0,
        "messages": [HumanMessage(content="Random text")],
        "patient_info": {},
        "symptoms": [],
        "extracted_symptoms": {},
        "possible_conditions": [],
        "analysis": {},
        "confidence_scores": {},
        "escalation_decision": False,
        "next_step": "intake"
    }
    
    final_state = await app.ainvoke(initial_state)
    
    # Diagnosis should not be called
    mock_agents["diagnosis"].invoke.assert_not_called()
    # Followup should be called
    mock_agents["followup"].invoke.assert_called_once()
    assert final_state["turn_count"] == 1
    
@pytest.mark.asyncio
async def test_workflow_max_followups(mock_agents):
    """Test that max followups correctly routes to handoff."""
    app = create_workflow()
    
    initial_state = {
        "session_id": "test_3",
        "turn_count": 3, # >= MAX_FOLLOWUPS (3)
        "messages": [],
        "patient_info": {},
        "symptoms": [],
        "extracted_symptoms": {},
        "possible_conditions": [],
        "analysis": {},
        "confidence_scores": {},
        "escalation_decision": False,
        "next_step": "intake"
    }
    
    final_state = await app.ainvoke(initial_state)
    
    # Because turn_count is 3, confidence_check immediately routes to handoff.
    assert final_state["next_step"] == "handoff"
