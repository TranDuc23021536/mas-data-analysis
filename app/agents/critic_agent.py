import json
import logging
from app.core.state import AgentState
from app.core.llm import invoke_with_retry, strip_code_fence
from app.core.fact_check import find_unverified_numbers

logger = logging.getLogger("mas.critic")

_VALID_TARGETS = ("sql", "analysis")

_SYSTEM_PROMPT = """Bạn là Critic Agent, lớp kiểm duyệt thứ hai. Lớp thứ nhất đã kiểm tra các con số bằng code và không phát hiện số bịa.

Đánh giá theo 3 tiêu chí:
1. SQL có trả lời đúng ý câu hỏi không (đúng bảng, đúng phép tính, đủ điều kiện lọc).
2. Insight có khớp với dữ liệu SQL trả về không, có suy diễn sai không.
3. Loại biểu đồ hiện tại có phù hợp với dữ liệu không (bỏ qua nếu không có biểu đồ).

Lưu ý: nếu SQL có LIMIT mà insight kết luận chỉ có 1 bản ghi hoặc 1 sản phẩm duy nhất trong toàn bộ dữ liệu chỉ vì kết quả trả về có 1 dòng thì đó là lỗi.

Trả về JSON gồm:
- approved: true nếu đạt cả 3 tiêu chí
- feedback: nếu approved là false thì nêu lỗi cụ thể, nếu true thì để chuỗi rỗng
- target_agent: nếu approved là false, chọn agent cần làm lại: "sql" nếu SQL sai ý câu hỏi, "analysis" nếu insight sai hoặc diễn giải sai

Chỉ trả về JSON, không giải thích thêm."""


def _reject(state: AgentState, feedback: str, target: str) -> AgentState:
    state["approved"] = False
    state["is_valid"] = False
    state["critic_feedback"] = feedback
    state["target_agent"] = target
    return state


def _approve(state: AgentState) -> AgentState:
    state["approved"] = True
    state["is_valid"] = True
    state["critic_feedback"] = ""
    state["target_agent"] = ""
    return state


def run_critic_agent(state: AgentState) -> AgentState:
    data = state.get("sql_result", [])
    insight = state.get("insight", "")
    state["fact_check_issues"] = []

    if state.get("sql_error"):
        logger.warning("Critic rejected: SQL error")
        return _reject(state, f"SQL lỗi: {state['sql_error']}", "sql")

    issues = find_unverified_numbers(insight, data)
    state["fact_check_issues"] = issues
    if issues:
        logger.warning(f"Critic layer 1 rejected, unverified numbers: {issues}")
        feedback = (
            f"Các số sau trong phần phân tích không khớp với dữ liệu SQL: {', '.join(issues)}. "
            "Chỉ dùng số có trong dữ liệu hoặc tính trực tiếp từ dữ liệu, làm tròn tối đa 2 chữ số thập phân."
        )
        return _reject(state, feedback, "analysis")

    question = state.get("rewritten_question") or state.get("question", "")
    user_prompt = (
        f"Câu hỏi: {question}\n\n"
        f"SQL: {state.get('sql_query', '')}\n\n"
        f"Dữ liệu (JSON):\n{json.dumps(data, ensure_ascii=False, default=str)}\n\n"
        f"Loại biểu đồ: {state.get('chart_type', 'none')}\n\n"
        f"Insight cần kiểm tra:\n{insight}"
    )

    content = invoke_with_retry([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])
    content = strip_code_fence(content, lang_hint="json")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Critic returned invalid JSON: {content}")
        return _approve(state)

    if parsed.get("approved", True):
        return _approve(state)

    target = parsed.get("target_agent", "analysis")
    if target not in _VALID_TARGETS:
        target = "analysis"
    return _reject(state, parsed.get("feedback", ""), target)