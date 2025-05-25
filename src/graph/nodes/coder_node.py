from src.graph.types import State
from langchain_core.runnables import RunnableConfig
from src.tools import python_repl_tool
from langgraph.types import Command
from typing import Literal
from src.graph.nodes.utils import (
    _setup_and_execute_agent_step
)
import logging
logger = logging.getLogger(__name__)


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")

    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool]
    )
    