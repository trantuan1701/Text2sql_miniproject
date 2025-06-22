from src.llm import llm
from src.prompt import planner_prompt
from .agentstate import AgentState
from langchain_core.messages import SystemMessage, HumanMessage


def planner_agent_node(state: AgentState) -> AgentState:
    formatted = planner_prompt.format(
        m_schema=state["m_schema"],
        question=state["question"],
        service_pk=state["service_pk"],
        comparison = state["comparison"]
    )

    try:
        resp = llm.invoke([
            SystemMessage(content="Bạn là Planner_agent"),
            HumanMessage(content=formatted)
        ])
        state["plan"] = resp.content
        state["messages"] = [resp]
    except Exception as e:
        state["error"] = f"planner_error: {e}"
    return state

