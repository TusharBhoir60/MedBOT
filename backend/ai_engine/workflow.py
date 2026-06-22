"""
LangGraph workflow definition for the MedBot CMAR process.
"""
from langgraph.graph import StateGraph, START, END

from ai_engine.state import SharedState
from ai_engine.agents.intake_agent import IntakeAgent
from ai_engine.agents.symptom_agent import SymptomAgent

def create_workflow() -> StateGraph:
    """
    Construct the CMAR workflow graph.
    Returns a compiled LangGraph application.
    """
    workflow = StateGraph(SharedState)
    
    # Initialize agents
    intake_agent = IntakeAgent()
    symptom_agent = SymptomAgent()
    
    # Define node functions (wrappers around the async agent invokes)
    async def run_intake(state: SharedState):
        return await intake_agent.invoke(state)
        
    async def run_symptom_analysis(state: SharedState):
        return await symptom_agent.invoke(state)
        
    async def run_handoff(state: SharedState):
        # Placeholder for handoff logic (e.g. notify a human agent)
        return {"next_step": "end"}
    
    # Add nodes to the graph
    workflow.add_node("intake", run_intake)
    workflow.add_node("analysis", run_symptom_analysis)
    workflow.add_node("handoff", run_handoff)
    
    # Define routing logic
    def route_after_intake(state: SharedState) -> str:
        next_step = state.get("next_step", "analysis")
        if next_step == "handoff":
            return "handoff"
        return "analysis"
        
    def route_after_analysis(state: SharedState) -> str:
        next_step = state.get("next_step", "end")
        if next_step == "handoff":
            return "handoff"
        return "end"
    
    # Define edges
    workflow.add_edge(START, "intake")
    
    # Conditional edge from intake
    workflow.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "analysis": "analysis",
            "handoff": "handoff"
        }
    )
    
    # Conditional edge from analysis
    workflow.add_conditional_edges(
        "analysis",
        route_after_analysis,
        {
            "handoff": "handoff",
            "end": END
        }
    )
    
    workflow.add_edge("handoff", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

# Singleton instance of the compiled workflow
app = create_workflow()
