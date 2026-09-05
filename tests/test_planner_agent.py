from app.agents.planner_agent import run_planner


def test_smalltalk_detected(mock_llm_response):
    with mock_llm_response('{"is_smalltalk": true, "rewritten_question": "Chào bạn", "needs_chart": false, "needs_forecast": false, "needs_anomaly": false}'):
        state = {"question": "Chào bạn", "chat_history": []}
        result = run_planner(state)
        assert result["is_smalltalk"] is True


def test_data_question_not_smalltalk(mock_llm_response):
    with mock_llm_response('{"is_smalltalk": false, "rewritten_question": "Doanh thu theo danh muc", "needs_chart": true, "needs_forecast": false, "needs_anomaly": false}'):
        state = {"question": "Doanh thu theo danh muc", "chat_history": []}
        result = run_planner(state)
        assert result["is_smalltalk"] is False
        assert result["needs_chart"] is True


def test_planner_handles_invalid_json_gracefully(mock_llm_response):
    with mock_llm_response("khong phai json"):
        state = {"question": "test", "chat_history": []}
        result = run_planner(state)
        assert result["is_smalltalk"] is False
        assert result["rewritten_question"] == "test"