import json
import logging
from app.core.state import AgentState
from app.core.llm import invoke_with_retry, strip_code_fence

logger = logging.getLogger("mas.critic")

_SYSTEM_PROMPT = """Bạn là Critic Agent. Nhiệm vụ: kiểm tra xem insight có khớp với dữ liệu SQL trả về không.

Trả về JSON gồm:
- is_valid: true nếu insight chính xác, không bịa số liệu, khớp với dữ liệu
- feedback: nếu is_valid là false, giải thích ngắn gọn lỗi sai để agent phân tích sửa lại; nếu true thì để chuỗi rỗng

Chỉ trả JSON, không giải thích thêm."""


def run_critic_agent(state: AgentState) -> AgentState:
    data = state.get("sql_result", [])
    insight = state.get("insight", "")

    if state.get("sql_error"):
        state["is_valid"] = False
        state["critic_feedback"] = f"SQL lỗi: {state['sql_error']}"
        logger.warning("Critic short-circuited due to SQL error")
        return state

    user_prompt = f"Dữ liệu (JSON):\n{json.dumps(data, ensure_ascii=False, default=str)}\n\nInsight cần kiểm tra:\n{insight}"

    content = invoke_with_retry([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])
    content = strip_code_fence(content, lang_hint="json")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Critic returned invalid JSON: {content}")
        parsed = {"is_valid": True, "feedback": ""}

    state["is_valid"] = parsed.get("is_valid", True)
    state["critic_feedback"] = parsed.get("feedback", "")

    logger.info(f"Critic verdict: is_valid={state['is_valid']}")

    return state