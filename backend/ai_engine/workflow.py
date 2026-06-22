"""
LangGraph workflow definition for the MedBot CMAR process.
"""
from langgraph.graph import StateGraph, START, END

from ai_engine.state import SharedState
from ai_engine.agents.intake_agent import IntakeAgent
from ai_engine.agents.symptom_agent import SymptomAgent
from ai_engine.agents.followup_agent import FollowUpAgent
from ai_engine.agents.diagnosis_agent import DiagnosisAgent
from ai_engine.nodes.confidence_aggregator import aggregate_confidence
from ai_engine.nodes.confidence_check import evaluate_confidence

def create_workflow() -> StateGraph:
    """
    Construct the CMAR workflow graph.
    Returns a compiled LangGraph application.
    """
    workflow = StateGraph(SharedState)
    
    # Initialize agents
    intake_agent = IntakeAgent()
    symptom_agent = SymptomAgent()
    followup_agent = FollowUpAgent()
    diagnosis_agent = DiagnosisAgent()
    
    # Define node wrappers
    async def run_intake(state: SharedState):
        return await intake_agent.invoke(state)
        
    async def run_symptom(state: SharedState):
        return await symptom_agent.invoke(state)
        
    async def run_followup(state: SharedState):
        return await followup_agent.invoke(state)
        
    async def run_diagnosis(state: SharedState):
        return await diagnosis_agent.invoke(state)
        
    async def run_handoff(state: SharedState):
        # Stub for human handoff
        return {"next_step": "end"}
        
    # Add nodes
    workflow.add_node("intake", run_intake)
    workflow.add_node("symptom", run_symptom)
    workflow.add_node("confidence_aggregator", aggregate_confidence)
    workflow.add_node("confidence_check", evaluate_confidence)
    workflow.add_node("diagnosis", run_diagnosis)
    workflow.add_node("followup", run_followup)
    workflow.add_node("handoff", run_handoff)
    
    # Main Pipeline Edges
    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "symptom")
    workflow.add_edge("symptom", "confidence_aggregator")
    workflow.add_edge("confidence_aggregator", "confidence_check")
    
    # Conditional Routing Logic from confidence_check
    def route_after_check(state: SharedState) -> str:
        return state.get("next_step", "handoff")
        
    workflow.add_conditional_edges(
        "confidence_check",
        route_after_check,
        {
            "diagnosis": "diagnosis",
            "followup": "followup",
            "handoff": "handoff"
        }
    )
    
    # Terminal Edges
    workflow.add_edge("diagnosis", END)
    workflow.add_edge("followup", END)
    workflow.add_edge("handoff", END)
    
    return workflow.compile()

app = create_workflow()
