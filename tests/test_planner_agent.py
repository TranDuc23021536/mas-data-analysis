from app.agents.planner_agent import run_planner


def test_smalltalk_detected():
    state = {"question": "Chào bạn", "chat_history": []}
    result = run_planner(state)
    assert result["is_smalltalk"] is True


def test_data_question_not_smalltalk():
    state = {"question": "Doanh thu theo danh mục là bao nhiêu?", "chat_history": []}
    result = run_planner(state)
    assert result["is_smalltalk"] is False