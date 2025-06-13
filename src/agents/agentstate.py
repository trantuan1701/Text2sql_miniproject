from typing import TypedDict, Annotated, Sequence, Optional, List, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain.schema import Document

class AgentState(TypedDict, total=False):
    # Shared state
    question: str
    messages: Annotated[List[BaseMessage], add_messages]
    intent: Optional[str]
    error: Optional[str]
    service_pk: Optional[str]
    mapping: str
    answer: Optional[str]

    #SQL-generator
    difference_type: Optional[str]
    comparison: Optional[str]
    plan: Optional[str]
    schema_lines: List[str]
    meta_lines: List[str]
    core_lines: List[str]
    m_schema: str
    