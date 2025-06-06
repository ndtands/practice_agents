import os
from langchain_core.runnables import RunnableConfig
from typing import Any, Optional
from dataclasses import dataclass, fields


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields."""

    max_plan_iterations: int = 1 # Maximum number of plan iterations
    max_step_num: int = 3 # Maximum number of steps in a plan
    max_search_results: int = 3  # Maximum number of search results
    mcp_settings: dict = None  # MCP settings, including dynamic loaded tools

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k,v in values.items() if v})
