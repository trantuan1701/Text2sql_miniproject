from datetime import datetime
from typing import Literal
from src.llm import llm
from src.prompt import pk_prompt
from .agentstate import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
import re
import json

def extract_json(text: str) -> dict:
    text = re.sub(r"^```[\w\s]*\n|\n```$", "", text.strip())
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("Không tìm thấy JSON")
    return json.loads(m.group(0))

def infer_comparison_type(date1: str, date2: str) -> Literal["2 tháng liên tiếp", "2 quý liên tiếp", "cùng kỳ năm trước", "không xác định"]:
    """
    Xác định mối quan hệ giữa 2 ngày:
    - Chính xác cùng ngày
    - Tháng/Quý/Năm cách nhau đúng 1 đơn vị
    """
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")

        if d2 > d1:
            d1, d2 = d2, d1

        same_day = d1.day == d2.day
        month_diff = (d1.year - d2.year) * 12 + (d1.month - d2.month)

        if same_day and month_diff == 1:
            return "2 tháng liên tiếp"

        if same_day and month_diff == 3:
            return "2 quý liên tiếp"

        if same_day and d1.month == d2.month and d1.year == d2.year + 1:
            return "cùng kỳ năm trước"

        return "không xác định"
    except Exception as e:
        print(f"Lỗi khi phân tích ngày: {e}")
        return "không xác định"



def context_extractor_node(state: AgentState) -> AgentState:
    try:
        resp = llm.invoke([
            SystemMessage(content="Nhận diện mã chỉ tiêu người dùng quan tâm"),
            HumanMessage(content=pk_prompt.format(
                mapping=state["mapping"],
                question=state["question"]
            ))
        ])

        result = extract_json(resp.content.strip())
        state["service_pk"] = result.get("service_pk")
        state["difference_type"] = result.get("difference_type")
        state["comparison"] = result.get("comparison")
        date1, date2 = result.get("date1"), result.get("date2")
        if date1 and date2:
            state["comparison"] = infer_comparison_type(date1, date2)
        

    except Exception as e:
        state["error"] = f"PK error: {e}"

    return state