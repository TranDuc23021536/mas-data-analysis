import json
from langchain_groq import ChatGroq
from app.core.config import settings
from app.core.state import AgentState

_llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0)

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
        return state

    user_prompt = f"Dữ liệu (JSON):\n{json.dumps(data, ensure_ascii=False, default=str)}\n\nInsight cần kiểm tra:\n{insight}"

    response = _llm.invoke([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    content = response.content.strip()
    if content.startswith("```"):
        content = content.strip("`").replace("json", "", 1).strip()

    parsed = json.loads(content)
    state["is_valid"] = parsed.get("is_valid", True)
    state["critic_feedback"] = parsed.get("feedback", "")

    return state