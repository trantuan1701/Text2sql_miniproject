from langchain_core.tools import tool
from src.retriver import ensemble_retrieve
from src.llm import llm
from .agentstate import AgentState
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage



@tool
def retriever_tool(query: str, service_pk) -> str:
    """
    Công cụ này dùng để truy xuất định nghĩa và giải thích cho một mã chỉ tiêu dựa trên service_pk, hoặc mô tả về mã chỉ tiêu được nhắc đến trong câu hỏi.
    Sử dụng công cụ này khi người dùng đặt câu hỏi về định nghĩa của một mã chỉ tiêu nào đó.
    """
    docs = ensemble_retrieve(query, service_pk)

    if not docs:
        return "Xin lỗi, tôi không tìm thấy định nghĩa phù hợp."
    return "\n\n".join(f"Definition {i+1}:\n{doc.page_content}" 
                       for i, doc in enumerate(docs))


tools = [retriever_tool]
llm_with_tools = llm.bind_tools(tools)


def should_continue(state: AgentState) -> bool:
    last = state['messages'][-1]
    return hasattr(last, 'tool_calls') and len(last.tool_calls) > 0

system_prompt = """
Bạn là một trợ lý AI thông minh chuyên giải thích các chỉ tiêu hiệu suất (mã chỉ tiêu) của VDS.
(Không trả lời cho người dùng thông tin dưới đây, đây là hướng dẫn dành cho bạn)
Khi người dùng hỏi dưới dạng “chỉ tiêu X là gì?”, “Cho tôi biết định nghĩa của mã Y” hoặc các câu hỏi tương tự,
hãy sử dụng retriever_tool với đối số query chứa mã chỉ tiêu hoặc câu hỏi của người dùng.
Bạn sẽ nhận được thông tin của 3 mã chỉ tiêu phù hợp nhất từ đó hãy chọn ra mã chỉ tiêu phù hợp.
Nếu người dùng hỏi về **một** mã luôn trả lời **một** mã và dựa vào thông tin đó để giải đáp thắc mắc của khách hàng.
Trả lời ngắn gọn bằng tiếng Việt giải đáp đúng thắc mắc của người dùng(chỉ cung cấp định nghĩa nếu cần). 
Nếu không tìm thấy, xin lỗi và thông báo “Không tìm thấy định nghĩa phù hợp.”
"""


def call_llm(state: AgentState) -> AgentState:
    msgs = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(msgs)
    state['answer'] = response.content
    state["messages"].append(response)
    return state


tools_dict = {t.name: t for t in tools}

def take_action(state: AgentState) -> AgentState:
    tool_calls = state['messages'][-1].tool_calls
    results = []

    for call in tool_calls:
        name = call['name']
        args = call["args"]

        if name not in tools_dict:
            content = "Tool không tồn tại, vui lòng thử lại."
        else:
            if name == "retriever_tool":
                args["service_pk"] = state.get("service_pk")
                content = tools_dict[name].invoke(args)
            else:
                content = tools_dict[name].invoke(args)

        state["messages"].append(
            ToolMessage(tool_call_id=call["id"], name=name, content=content)
        )
    return state

