from langgraph.graph import StateGraph, END
from operator import add as add_messages
from .agentstate import AgentState
from .router import router_node
from .schema_selector import schema_selector_node
from .sql_generator import gen_sql_node
from .planner_agent import planner_agent_node
from .context_extractor import context_extractor_node
from .business_qa import call_llm, take_action, should_continue



graph = StateGraph(AgentState)

graph.add_node("context_extractor", context_extractor_node)
graph.add_node("planner_agent", planner_agent_node)
graph.add_node("schema_selector", schema_selector_node)
graph.add_node("generate_sql", gen_sql_node)
graph.add_node("llm_business_qa", call_llm)
graph.add_node("execute_tool", take_action)
graph.add_node("router", router_node)

graph.set_entry_point("context_extractor")
graph.add_edge("schema_selector", "planner_agent")
graph.add_edge("planner_agent", "generate_sql")
graph.add_edge("execute_tool", "llm_business_qa")
graph.add_edge("context_extractor", "router")
graph.add_conditional_edges(
    "router",
    lambda state: state["intent"],
    {
        "business": "llm_business_qa",
        "sql": "schema_selector",
    }
)
graph.add_edge("generate_sql", END)
graph.add_conditional_edges(
    "llm_business_qa",
    should_continue,
    {True: "execute_tool", False: END}
)

app = graph.compile()

