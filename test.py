import asyncio
from src.graph.nodes import researcher_node
from src.graph.types import State
from langchain_core.runnables import RunnableConfig
from src.prompts.planner_model import Plan, Step, StepType
from langchain_core.messages import HumanMessage

async def main():
    # Tạo một step research mẫu
    step = Step(
        need_web_search=True,
        title="Tìm hiểu về AI",
        description="Thu thập thông tin tổng quan về AI, các ứng dụng và xu hướng hiện tại.",
        step_type=StepType.RESEARCH,
        execution_res=None
    )
    # Tạo một plan mẫu
    plan = Plan(
        locale="vi-VN",
        has_enough_context=True,
        thought="Cần tổng hợp thông tin về AI.",
        title="Kế hoạch nghiên cứu AI",
        steps=[step]
    )
    # Tạo state đầu vào cho node
    state = State(
        messages=[HumanMessage(content="Hãy nghiên cứu về AI")],
        locale="vi-VN",
        observations=[],
        plan_iterations=0,
        current_plan=plan,
        final_report="",
        auto_accepted_plan=True,
        enable_background_investigation=False,
        background_investigation_results=None
    )
    # Tạo config đơn giản
    config = RunnableConfig(
        configurable={
            "thread_id": "test",
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "mcp_settings": {"servers": {}},
        },
        recursion_limit=10,
    )
    # Gọi node researcher_node
    result = await researcher_node(state, config)
    print("Kết quả researcher_node:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())