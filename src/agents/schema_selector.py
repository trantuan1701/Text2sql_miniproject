from src.llm import llm
from src.prompt import sql_prompt, planner_prompt
from .agentstate import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
import re

def schema_selector(state):
    schema_lines, meta_lines, core_lines = state["schema_lines"], state["meta_lines"], state["core_lines"]
    def extract_column_names(lines):
        return [
            m.group(1)
            for line in lines
            if (m := re.search(r"^(\w+):", line))
        ]

    def filter_columns(all_fields, state):
        diff = state.get("difference_type")
        comp = state.get("comparison")
        suffix = "_DELTA" if diff == "DELTA" else "_PERCENT" if diff == "PERCENT" else None

        comparison_map = {
            "2 tháng liên tiếp": ["SPM","SPDM"],
            "2 quý liên tiếp": ["SPQ"],
            "cùng kỳ năm trước": ["SPMY", "SPQY", "SPY"]
        }

        if not suffix or not comp or comp not in comparison_map:
            return []

        prefixes = comparison_map[comp]
        return [
            f for f in all_fields
            if (f.split("_",1)[0] in prefixes) and f.endswith(suffix)
        ]

    def select_schema_lines_by_fields(schema_lines, fields):
        return [
            line
            for line in schema_lines
            if any(line.strip().startswith(f"{field}:") for field in fields)
        ]

    def generate_full_schema(meta, core, filtered):
        all_lines = meta + core + filtered
        return "# Table: CHATBOT_KTDL_TARGETS_REVENUE\n[\n  " + ",\n  ".join(all_lines) + "\n]"

    all_fields = extract_column_names(schema_lines)
    selected_fields = filter_columns(all_fields, state)
    selected_lines = select_schema_lines_by_fields(schema_lines, selected_fields)
    return generate_full_schema(meta_lines, core_lines, selected_lines)


def schema_selector_node(state: AgentState) -> AgentState:
    state["m_schema"] = schema_selector(state)
    return state