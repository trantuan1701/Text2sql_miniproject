from src.llm import llm
from src.prompt import sql_prompt
from .agentstate import AgentState
from langchain_core.messages import SystemMessage, HumanMessage


def gen_sql_node(state: AgentState) -> AgentState:
    try:
        resp = llm.invoke([
            SystemMessage(content=(
                "Bạn là chuyên gia SQL. "
                "Chỉ trả về câu lệnh SQL hoàn chỉnh."
            )),
            HumanMessage(content=sql_prompt.format(
                plan=state["plan"],
                question=state["question"]
            ))
        ])
        state["answer"] = resp.content
        state["messages"] = [resp]
    except Exception as e:
        state["error"] = f"SQL error: {e}"
    return state