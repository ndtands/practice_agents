from src.graph.types import State
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from typing import Literal
from src.config.configuration import Configuration
from src.tools.search import LoggedTavilySearch
import logging
import json
logger = logging.getLogger(__name__)

def background_investigation_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner"]]:
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content

    searched_content = LoggedTavilySearch(
        max_results=configurable.max_search_results
    ).invoke({"query": query})
    background_investigation_results = None
    if isinstance(searched_content, list):
        background_investigation_results = [
            {"title": elem["title"], "content": elem["content"]}
            for elem in searched_content
        ]
    else:
        logger.error(
            f"Tavily search returned malformed response: {searched_content}"
        )

    return Command(
        update={
            "background_investigation_results": json.dumps(
                background_investigation_results, ensure_ascii=False
            )
        },
        goto="planner",
    )