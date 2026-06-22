"""
Chat router exposing the LangGraph CMAR workflow.
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from ai_engine.workflow import app as chat_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# In-memory session store for Sprint 2.1
session_store: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID for the conversation")
    message: str = Field(..., description="The user's message")
    patient_info: Dict[str, Any] = Field(default_factory=dict, description="Current patient demographics")
    symptoms: list[str] = Field(default_factory=list, description="Raw symptoms")
    
@router.post("/invoke", response_model=Dict[str, Any])
async def invoke_chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Invoke the MedBot AI workflow with a user message.
    Passes the message through the Intake and Symptom Analysis agents.
    """
    logger.info("Received chat invoke request")
    try:
        session_id = request.session_id
        
        if session_id in session_store:
            # Resume existing session
            current_state = session_store[session_id]
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
        
        # Persist session
        session_store[session_id] = final_state
        
        # Serialize messages for the JSON response
        if "messages" in final_state:
            final_state["messages"] = [
                {"role": m.type, "content": m.content} if hasattr(m, "type") else str(m)
                for m in final_state["messages"]
            ]
            
        return final_state
        
    except Exception as e:
        logger.error(f"Error during workflow execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal AI Engine Error")
