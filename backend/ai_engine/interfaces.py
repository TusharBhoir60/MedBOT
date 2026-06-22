"""
Interfaces and base classes for AI Agents.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from ai_engine.state import SharedState

class AgentInterface(ABC):
    """Abstract base class for all AI agents in the LangGraph workflow."""
    
    @abstractmethod
    async def invoke(self, state: SharedState) -> Dict[str, Any]:
        """
        Process the current state and return state updates.
        
        Args:
            state: The current SharedState of the LangGraph workflow.
            
        Returns:
            A dictionary containing the state keys to update.
        """
        pass
