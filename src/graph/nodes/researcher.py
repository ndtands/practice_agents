from src.graph.types import State
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from typing import Literal
from src.config.configuration import Configuration
from src.graph.nodes.utils import (
    _setup_and_execute_agent_step
)
from src.tools import get_web_search_tool, crawl_tool
import logging
logger = logging.getLogger(__name__)

async def researcher_node(
        state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        [get_web_search_tool(configurable.max_search_results), crawl_tool],
    )
