import json
import logging
from app.core.state import AgentState
from app.core.llm import invoke_with_retry

logger = logging.getLogger("mas.responder")

_SYSTEM_PROMPT = """Bạn là Responder Agent. Viết lại insight dưới đây thành một câu trả lời hội thoại tự nhiên bằng tiếng Việt, giống người đang trò chuyện, không phải bản liệt kê máy móc.

Quy tắc bắt buộc:
- KHÔNG được thêm, đổi, hay tính lại bất kỳ con số nào ngoài các số đã có trong insight. Chỉ diễn đạt lại câu chữ.
- Nếu có ghi chú về biểu đồ/dự báo/bất thường ở dưới, hãy lồng ghép tự nhiên vào câu trả lời (ví dụ: "mình vẽ kèm biểu đồ cột để bạn dễ so sánh"), không viết thành dòng riêng kiểu "(Đã tạo biểu đồ...)".
- Giữ độ dài tương đương insight gốc, không thêm thông tin mới, không thêm lời chào/lời kết thừa."""


def _build_notes(state: AgentState) -> str:
    notes = []
    if state.get("chart_type", "none") != "none":
        notes.append(f"Đã tạo biểu đồ dạng {state['chart_type']}.")
    if state.get("forecast_result"):
        notes.append(f"Có dự báo xu hướng: {state.get('forecast_trend', '')}.")
    if state.get("anomaly_result"):
        notes.append(f"Phát hiện {len(state['anomaly_result'])} điểm bất thường.")
    return " ".join(notes)


def run_responder_agent(state: AgentState) -> AgentState:
    if state.get("is_smalltalk"):
        state["final_answer"] = "Chào bạn! Mình có thể giúp bạn phân tích dữ liệu kinh doanh, bạn muốn hỏi gì?"
        return state

    if state.get("sql_error"):
        state["final_answer"] = f"Xin lỗi, mình không thể truy vấn được dữ liệu này. Lỗi: {state['sql_error']}"
        return state

    insight = state.get("insight", "")
    notes = _build_notes(state)

    if not notes:
        state["final_answer"] = insight
        return state

    user_prompt = f"Insight:\n{insight}\n\nGhi chú bổ sung:\n{notes}"

    try:
        final_answer = invoke_with_retry([
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ])
        state["final_answer"] = final_answer
    except Exception as e:
        logger.error(f"Responder LLM call failed, falling back to concatenation: {e}")
        state["final_answer"] = f"{insight}\n\n{notes}"

    return state