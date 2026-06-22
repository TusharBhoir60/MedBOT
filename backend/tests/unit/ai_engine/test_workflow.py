import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage

from ai_engine.state import SharedState, ConfidenceSchema
from ai_engine.workflow import create_workflow

@pytest.fixture
def mock_intake_agent():
    with patch("ai_engine.workflow.IntakeAgent") as MockAgent:
        agent = MockAgent.return_value
        agent.invoke = AsyncMock()
        yield agent

@pytest.fixture
def mock_symptom_agent():
    with patch("ai_engine.workflow.SymptomAgent") as MockAgent:
        agent = MockAgent.return_value
        agent.invoke = AsyncMock()
        yield agent

@pytest.mark.asyncio
async def test_workflow_successful_path(mock_intake_agent, mock_symptom_agent):
    """Test the workflow when both agents have high confidence."""
    
    mock_intake_agent.invoke.return_value = {
        "patient_info": {"age": 30},
        "symptoms": ["headache"],
        "confidence_scores": {
            "intake": ConfidenceSchema(score=0.9, reasoning="Clear")
        },
        "escalation_decision": False,
        "next_step": "analysis"
    }
    
    mock_symptom_agent.invoke.return_value = {
        "extracted_symptoms": ["Headache"],
        "possible_conditions": ["Migraine"],
        "analysis": "Take rest",
        "confidence_scores": {
            "symptom_analysis": ConfidenceSchema(score=0.85, reasoning="Clear symptoms")
        },
        "escalation_decision": False,
        "next_step": "end"
    }
    
    app = create_workflow()
    initial_state = {
        "messages": [HumanMessage(content="I have a headache.")],
        "patient_info": {},
        "symptoms": [],
        "confidence_scores": {},
        "escalation_decision": False,
        "next_step": "intake"
    }
    
    final_state = await app.ainvoke(initial_state)
    
    # Assertions
    assert final_state["patient_info"] == {"age": 30}
    assert final_state["extracted_symptoms"] == ["Headache"]
    assert "symptom_analysis" in final_state["confidence_scores"]
    assert final_state["escalation_decision"] is False

@pytest.mark.asyncio
async def test_workflow_handoff_path(mock_intake_agent, mock_symptom_agent):
    """Test the workflow when the intake agent requires handoff."""
    
    mock_intake_agent.invoke.return_value = {
        "confidence_scores": {
            "intake": ConfidenceSchema(score=0.2, reasoning="Unclear")
        },
        "escalation_decision": True,
        "next_step": "handoff"
    }
    
    app = create_workflow()
    initial_state = {
        "messages": [HumanMessage(content="Random text")],
        "patient_info": {},
        "symptoms": [],
        "confidence_scores": {},
        "escalation_decision": False,
        "next_step": "intake"
    }
    
    final_state = await app.ainvoke(initial_state)
    
    # Symptom agent should not be called if intake routes to handoff
    mock_symptom_agent.invoke.assert_not_called()
    assert final_state["escalation_decision"] is True
