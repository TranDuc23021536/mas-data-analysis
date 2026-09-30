import json
import logging
from decimal import Decimal
from app.core.state import AgentState
from app.core.llm import invoke_with_retry, strip_code_fence

logger = logging.getLogger("mas.visualization")

_TIME_NAME_HINTS = ("date", "month", "year", "time", "period", "quarter", "week")
_VALID_TYPES = ("bar", "line", "pie", "scatter", "table")

_SYSTEM_PROMPT = """Bạn là Visualization Agent. Dựa trên câu hỏi và các cột dữ liệu, đề xuất loại biểu đồ phù hợp nhất.

Các loại: bar (so sánh giữa các nhóm), line (xu hướng theo thời gian), pie (tỷ trọng, tối đa 8 phần), scatter (mối quan hệ giữa 2 đại lượng số), table (không phù hợp để vẽ).

Trả về JSON:
- chart_type: một trong bar/line/pie/scatter/table
- x_col: tên cột dùng làm trục hoành/nhãn (bỏ trống nếu chart_type là table)
- y_col: tên cột số liệu dùng để vẽ (bỏ trống nếu chart_type là table)

Chỉ trả JSON, không giải thích thêm."""


def _is_time_like_name(name: str) -> bool:
    lower = name.lower()
    return any(hint in lower for hint in _TIME_NAME_HINTS)


def _is_numeric(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float, Decimal))


def _column_kinds(row: dict) -> dict:
    kinds = {}
    for key, value in row.items():
        if _is_time_like_name(key):
            kinds[key] = "time"
        elif _is_numeric(value):
            kinds[key] = "numeric"
        else:
            kinds[key] = "text"
    return kinds


def _numeric_column_names(data: list) -> set:
    if not data:
        return set()
    return {k for k, v in data[0].items() if _is_numeric(v)}


def _rule_based_selection(data: list):
    if not data:
        return "none", None, None

    kinds = _column_kinds(data[0])
    time_cols = [c for c, k in kinds.items() if k == "time"]
    text_cols = [c for c, k in kinds.items() if k == "text"]
    numeric_cols = [c for c, k in kinds.items() if k == "numeric"]

    if time_cols and numeric_cols:
        return "line", time_cols[0], numeric_cols[0]
    if len(data) <= 8 and text_cols and numeric_cols:
        return "bar", text_cols[0], numeric_cols[0]
    if len(text_cols) == 1 and len(numeric_cols) == 1 and len(data) <= 6:
        return "pie", text_cols[0], numeric_cols[0]
    if len(numeric_cols) >= 2 and not text_cols:
        return "scatter", numeric_cols[0], numeric_cols[1]
    return "table", None, None


def _validate_proposal(proposal: dict, data: list):
    chart_type = proposal.get("chart_type")
    if chart_type not in _VALID_TYPES:
        return None
    if chart_type == "table":
        return "table", None, None

    x_col = proposal.get("x_col")
    y_col = proposal.get("y_col")
    if not x_col or not y_col:
        return None

    cols = set(data[0].keys())
    if x_col not in cols or y_col not in cols:
        return None

    numeric_cols = _numeric_column_names(data)
    if y_col not in numeric_cols:
        return None
    if chart_type == "scatter" and x_col not in numeric_cols:
        return None
    if chart_type == "pie" and len(data) > 8:
        return None

    return chart_type, x_col, y_col


def _describe_columns(data: list) -> str:
    kinds = _column_kinds(data[0])
    return ", ".join(f"{k} ({v})" for k, v in kinds.items())


def run_visualization_agent(state: AgentState) -> AgentState:
    if not state.get("needs_chart") and not state.get("chart_only"):
        state["chart_type"] = "none"
        state["chart_data"] = []
        return state

    data = state.get("sql_result", [])
    if not data:
        state["chart_type"] = "none"
        state["chart_data"] = []
        return state

    requested = state.get("requested_chart_type", "")
    if requested in _VALID_TYPES:
        if requested == "table":
            state["chart_type"] = "table"
            state["chart_data"] = data
            return state
        _, x_col, y_col = _rule_based_selection(data)
        chart_type = requested if x_col and y_col else "table"
    else:
        question = state.get("rewritten_question") or state.get("question", "")
        user_prompt = (
            f"Câu hỏi: {question}\n\n"
            f"Các cột và kiểu dữ liệu: {_describe_columns(data)}\n\n"
            f"Mẫu dữ liệu (tối đa 5 dòng): {json.dumps(data[:5], ensure_ascii=False, default=str)}"
        )
        try:
            content = invoke_with_retry([
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ])
            proposal = json.loads(strip_code_fence(content, lang_hint="json"))
        except Exception as e:
            logger.warning(f"Visualization LLM proposal failed, falling back to rule-based: {e}")
            proposal = {}

        validated = _validate_proposal(proposal, data)
        if validated:
            chart_type, x_col, y_col = validated
            logger.info(f"Using LLM-proposed chart: {chart_type} ({x_col}/{y_col})")
        else:
            logger.info("LLM proposal invalid or missing, using rule-based fallback")
            chart_type, x_col, y_col = _rule_based_selection(data)

    if chart_type == "table" or not x_col or not y_col:
        state["chart_type"] = "table"
        state["chart_data"] = data
        return state

    state["chart_type"] = chart_type
    state["chart_data"] = [{x_col: row.get(x_col), y_col: row.get(y_col)} for row in data]
    return state