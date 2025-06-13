from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from .agentstate import AgentState
from src.prompt import intent_prompt
from src.llm import llm

def router_node(state: AgentState) -> AgentState:
    try:
        response = llm.invoke([
            SystemMessage(content="Nhiệm vụ của bạn là phân loại câu hỏi của người dùng"),
            HumanMessage(content=intent_prompt.format(question = state["question"])),
        ])

        intent = response.content.strip().lower()
        state["intent"] = intent
    except Exception as e:
        print(e)
        state["error"] = f"Intent classification error {e}"
        state["intent"] = "business"  # fallback
    return state