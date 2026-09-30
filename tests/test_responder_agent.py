from unittest.mock import patch

from app.agents.responder_agent import run_responder_agent


def test_responder_smalltalk_skips_llm():
    state = {"is_smalltalk": True}
    with patch("app.agents.responder_agent.invoke_with_retry") as llm:
        result = run_responder_agent(state)
        llm.assert_not_called()
    assert result["final_answer"] != ""


def test_responder_sql_error_skips_llm():
    state = {"is_smalltalk": False, "sql_error": "connection refused"}
    with patch("app.agents.responder_agent.invoke_with_retry") as llm:
        result = run_responder_agent(state)
        llm.assert_not_called()
    assert "lỗi" in result["final_answer"].lower()


def test_responder_no_notes_returns_insight_unchanged():
    state = {"is_smalltalk": False, "sql_error": None, "insight": "Insight ABC", "chart_type": "none"}
    with patch("app.agents.responder_agent.invoke_with_retry") as llm:
        result = run_responder_agent(state)
        llm.assert_not_called()
    assert result["final_answer"] == "Insight ABC"


def test_responder_rewrites_with_notes_via_llm(mock_llm_response):
    state = {
        "is_smalltalk": False,
        "sql_error": None,
        "insight": "Insight ABC",
        "chart_type": "bar",
        "forecast_result": [],
        "anomaly_result": [],
    }
    with mock_llm_response("Bản viết lại tự nhiên có nhắc biểu đồ."):
        result = run_responder_agent(state)
    assert result["final_answer"] == "Bản viết lại tự nhiên có nhắc biểu đồ."


def test_responder_falls_back_if_llm_fails():
    state = {
        "is_smalltalk": False,
        "sql_error": None,
        "insight": "Insight ABC",
        "chart_type": "bar",
        "forecast_result": [],
        "anomaly_result": [],
    }
    with patch("app.agents.responder_agent.invoke_with_retry", side_effect=RuntimeError("timeout")):
        result = run_responder_agent(state)
    assert "Insight ABC" in result["final_answer"]
    assert "bar" in result["final_answer"]