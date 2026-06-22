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

class ChatRequest(BaseModel):
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
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "patient_info": request.patient_info,
            "symptoms": request.symptoms,
            "confidence_scores": {},
            "escalation_decision": False,
            "next_step": "intake"
        }
        
        # Invoke the LangGraph workflow
        final_state = await chat_workflow.ainvoke(initial_state)
        
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
