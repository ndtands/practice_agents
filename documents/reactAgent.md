# React Agent 

- React (Reasoning + Action) in the Loop:
    + **Reasoning**: LLM anslysis the user's input, reasons about how to solve the problem, and decides whether to call a tool.
    + **Action**: If needed, the agent invokes one or more tools and receives results (observations).
    + **Observation**: The tool's ouput is fed back to the LLM for further resoning or to geneerate a final response.
    + The loop continues until the LLM determines no further tool calls are needed and provides a final answer
- State Graph:
    + Uses a graph to manage the workflow, consisting of:
        + Nodes: Represent actions (e.g., calling the LLM , executng a tool).
        + Edges: Define the control flow between nodes.
        + State: A object storing the agent's current state, typically a list of messages of additional information like conversation history or intermediate steps.
- Human-in-the-Loop(Optinal):
    - Suport integrating human feedback into the loop to review, approve, or edit eht agent's response before final output
- Memory:
    - By default, the ReAct Agent is stateless (no conversation history). You can add a checkpoint to store conversation history, enabling the agent to respond based on prior context.

In Langgraph:
```
def create_react_agent(
    model: Union[str, LanguageModelLike],
    tools: Union[Sequence[Union[BaseTool, Callable, dict[str, Any]]], ToolNode],
    *,
    prompt: Optional[Prompt] = None,
    response_format: Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ] = None,
    pre_model_hook: Optional[RunnableLike] = None,
    post_model_hook: Optional[RunnableLike] = None,
    state_schema: Optional[StateSchemaType] = None,
    config_schema: Optional[Type[Any]] = None,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    interrupt_before: Optional[list[str]] = None,
    interrupt_after: Optional[list[str]] = None,
    debug: bool = False,
    version: Literal["v1", "v2"] = "v2",
    name: Optional[str] = None,
) -> CompiledGraph:
```

Limitation: 
    - If workflow complicate -> mabe need create new custom workflow instead of use reactAgent.
    
