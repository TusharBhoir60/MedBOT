"""
LLM Provider Abstraction.

Centralizes the instantiation of Language Models to allow easy swapping
between OpenAI, Anthropic, or local models without modifying the agents.
"""
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from core.config import settings

def get_llm_provider(model_name: Optional[str] = None, temperature: float = 0.0) -> BaseChatModel:
    """Factory function to get the configured LLM provider.
    
    Args:
        model_name: The name of the model to use. Defaults to settings.ai.model_primary.
        temperature: The sampling temperature. Defaults to 0.0.
        
    Returns:
        An instance of BaseChatModel configured for the requested provider.
    """
    model = model_name or settings.ai.model_primary
    
    # Currently hardcoded to return OpenAI, but centralized here so we can
    # easily add branching logic for Anthropic or others based on settings.
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.ai.openai_api_key
    )
