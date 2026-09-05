import json
import logging
from app.core.state import AgentState
from app.core.llm import invoke_with_retry, strip_code_fence

logger = logging.getLogger("mas.planner")

_SYSTEM_PROMPT = """Bạn là Planner Agent trong hệ thống phân tích dữ liệu đa tác tử.
Nhiệm vụ: phân tích câu hỏi người dùng và trả về JSON với các trường:
- is_smalltalk: true nếu câu hỏi chỉ là xã giao (chào hỏi, cảm ơn, không liên quan dữ liệu)
- rewritten_question: viết lại câu hỏi đầy đủ ngữ nghĩa dựa trên lịch sử hội thoại (nếu câu hỏi là câu tiếp nối như "còn quý trước thì sao"), nếu không cần viết lại thì giữ nguyên câu hỏi gốc
- needs_chart: true nếu câu hỏi cần biểu đồ trực quan
- needs_forecast: true nếu câu hỏi cần dự báo xu hướng tương lai
- needs_anomaly: true nếu câu hỏi cần phát hiện bất thường

Chỉ trả về JSON, không giải thích thêm."""


def run_planner(state: AgentState) -> AgentState:
    history_text = ""
    for turn in state.get("chat_history", [])[-5:]:
        history_text += f"{turn['role']}: {turn['content']}\n"

    user_prompt = f"Lịch sử hội thoại:\n{history_text}\n\nCâu hỏi hiện tại: {state['question']}"

    logger.info(f"Planning for question: {state['question'][:80]}")

    content = invoke_with_retry([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])
    content = strip_code_fence(content, lang_hint="json")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Planner returned invalid JSON: {content}")
        parsed = {}

    state["is_smalltalk"] = parsed.get("is_smalltalk", False)
    state["rewritten_question"] = parsed.get("rewritten_question", state["question"])
    state["needs_chart"] = parsed.get("needs_chart", False)
    state["needs_forecast"] = parsed.get("needs_forecast", False)
    state["needs_anomaly"] = parsed.get("needs_anomaly", False)

    return state