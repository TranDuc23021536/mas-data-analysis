from decimal import Decimal
from app.core.state import AgentState


def _guess_chart_type(data: list) -> str:
    if not data:
        return "none"

    first_row = data[0]
    numeric_cols = [k for k, v in first_row.items() if isinstance(v, (int, float, Decimal))]
    text_cols = [k for k, v in first_row.items() if isinstance(v, str)]
    date_like_cols = [k for k in first_row.keys() if "date" in k.lower() or "month" in k.lower() or "time" in k.lower()]

    if date_like_cols and numeric_cols:
        return "line"
    if len(data) <= 8 and text_cols and numeric_cols:
        return "bar"
    if len(text_cols) == 1 and len(numeric_cols) == 1 and len(data) <= 6:
        return "pie"
    return "table"


def run_visualization_agent(state: AgentState) -> AgentState:
    if not state.get("needs_chart"):
        state["chart_type"] = "none"
        state["chart_data"] = []
        return state

    data = state.get("sql_result", [])
    state["chart_type"] = _guess_chart_type(data)
    state["chart_data"] = data
    return state