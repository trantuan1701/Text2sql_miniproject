from src.agents.agentstate import AgentState
from src.agents.buildgraph import app
from langchain_core.messages import HumanMessage, AIMessage
from data.schema import schema_lines, meta_lines, core_lines #internal data(hiding)
with open("src/schema/service_pk.txt","r", encoding="utf-8") as f:
    mapping = f.read().strip()
with open("src/schema/m_schema.txt", "r", encoding="utf-8") as f:
    m_schema = f.read().strip()

def get_chat_response(user_input: str) -> str:
    initial_state = AgentState({
        "question" : user_input,
        "schema_lines": schema_lines,
        "meta_lines": meta_lines,
        "core_lines" : core_lines,
        "mapping": mapping,
        "m_schema": m_schema,
        "messages": [HumanMessage(content=user_input)],
    })
    out = app.invoke(initial_state)
    #msgs = out["messages"]

    # ai_msgs = [m for m in msgs if isinstance(m, AIMessage)]
    return out.get("answer")
    