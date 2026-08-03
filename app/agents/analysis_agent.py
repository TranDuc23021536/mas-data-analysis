import json
from langchain_groq import ChatGroq
from app.core.config import settings
from app.core.state import AgentState

_llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0)

_SYSTEM_PROMPT = """Bạn là Analysis Agent. Dựa trên câu hỏi và dữ liệu kết quả truy vấn SQL, hãy rút ra insight ngắn gọn.

Yêu cầu bắt buộc:
- Chỉ dùng số liệu có trong dữ liệu được cung cấp, không được bịa thêm số liệu.
- Nếu dữ liệu rỗng, nói rõ không có dữ liệu phù hợp.
- Trả lời bằng tiếng Việt, 2-4 câu, tập trung vào điểm nổi bật nhất (giá trị cao nhất/thấp nhất, xu hướng, so sánh)."""


def run_analysis_agent(state: AgentState) -> AgentState:
    question = state.get("rewritten_question") or state["question"]
    data = state.get("sql_result", [])

    user_prompt = f"Câu hỏi: {question}\n\nDữ liệu (JSON):\n{json.dumps(data, ensure_ascii=False, default=str)}"

    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    state["insight"] = response.content.strip()
    return state