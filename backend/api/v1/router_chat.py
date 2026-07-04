"""
Chat router exposing the LangGraph CMAR workflow.
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ai_engine.workflow import app as chat_workflow
from ai_engine.safety.response_validator import SafetyViolation
from api.dependencies import ChatServiceDep
import copy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID for the conversation")
    message: str = Field(..., description="The user's message")
    patient_info: Dict[str, Any] = Field(default_factory=dict, description="Current patient demographics")
    symptoms: list[str] = Field(default_factory=list, description="Raw symptoms")
    
@router.post("/invoke", response_model=Dict[str, Any])
async def invoke_chat(
    request: ChatRequest,
    chat_service: ChatServiceDep
) -> Dict[str, Any]:
    """
    Invoke the MedBot AI workflow with a user message.
    Passes the message through the Intake and Symptom Analysis agents.
    """
    logger.info("Received chat invoke request")
    try:
        session_id = request.session_id
        
        current_state = await chat_service.get_session_state(session_id)
        if current_state:
            # Resume existing session
            
            # Deserialize messages
            msgs = []
            for m in current_state.get("messages", []):
                if isinstance(m, dict):
                    role = m.get("role")
                    content = m.get("content", "")
                    if role == "human": msgs.append(HumanMessage(content=content))
                    elif role == "ai": msgs.append(AIMessage(content=content))
                    elif role == "system": msgs.append(SystemMessage(content=content))
                    else: msgs.append(HumanMessage(content=content))
                else:
                    msgs.append(m)
            current_state["messages"] = msgs
            current_state["messages"].append(HumanMessage(content=request.message))
            
            # Update any explicitly provided new info
            if request.patient_info:
                current_state["patient_info"].update(request.patient_info)
            if request.symptoms:
                current_state["symptoms"].extend(request.symptoms)
        else:
            # Initialize new session
            current_state = {
                "session_id": session_id,
                "turn_count": 0,
                "messages": [HumanMessage(content=request.message)],
                "patient_info": request.patient_info,
                "symptoms": request.symptoms,
                "extracted_symptoms": {},
                "possible_conditions": [],
                "analysis": {},
                "confidence_scores": {},
                "escalation_decision": False,
                "next_step": "intake"
            }
        
        # Invoke the LangGraph workflow
        final_state = await chat_workflow.ainvoke(current_state)
        
        # We must serialize the state to JSON before storing
        state_to_store = copy.deepcopy(final_state)
        if "messages" in state_to_store:
            state_to_store["messages"] = [
                {"role": m.type, "content": m.content} if hasattr(m, "type") else m
                for m in state_to_store["messages"]
            ]
            
        # Persist session
        await chat_service.save_session_state(session_id, state_to_store)
        
        return state_to_store
        
    except SafetyViolation as sv:
        logger.error(f"Safety violation blocked response: {sv}")
        raise HTTPException(status_code=500, detail="Response blocked by safety validator. Please consult a human clinician.")
    except Exception as e:
        logger.error(f"Error during workflow execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal AI Engine Error")
