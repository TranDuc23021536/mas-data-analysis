from app.core.state import AgentState


def run_responder_agent(state: AgentState) -> AgentState:
    if state.get("is_smalltalk"):
        state["final_answer"] = "Chào bạn! Mình có thể giúp bạn phân tích dữ liệu kinh doanh, bạn muốn hỏi gì?"
        return state

    if state.get("sql_error"):
        state["final_answer"] = f"Xin lỗi, mình không thể truy vấn được dữ liệu này. Lỗi: {state['sql_error']}"
        return state

    answer = state.get("insight", "")
    if state.get("chart_type", "none") != "none":
        answer += f"\n\n(Đã tạo biểu đồ dạng {state['chart_type']} để minh họa)"

    state["final_answer"] = answer
    return state