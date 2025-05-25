from pathlib import Path
from typing import Any, Dict
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from src.config.agents import LLMType
from src.config.llms import base_model

# Cache for LLM instances
_llm_cache: dict[LLMType, ChatOpenAI] = {}

def get_llm_by_type(
    llm_type: LLMType,
) -> ChatOpenAI:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    llm = None
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]
    
    if llm_type == "basic":
        llm = base_model
    # update to cache
    _llm_cache[llm_type] = llm
    return llm