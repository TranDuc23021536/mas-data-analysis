from app.agents.responder_agent import run_responder_agent


def test_responder_smalltalk():
    state = {"is_smalltalk": True}
    result = run_responder_agent(state)
    assert result["final_answer"] != ""


def test_responder_sql_error():
    state = {"is_smalltalk": False, "sql_error": "connection refused"}
    result = run_responder_agent(state)
    assert "loi" in result["final_answer"].lower() or "lỗi" in result["final_answer"].lower()


def test_responder_appends_chart_note():
    state = {"is_smalltalk": False, "sql_error": None, "insight": "Insight ABC", "chart_type": "bar"}
    result = run_responder_agent(state)
    assert "Insight ABC" in result["final_answer"]
    assert "bar" in result["final_answer"]


def test_responder_appends_forecast_and_anomaly_notes():
    state = {
        "is_smalltalk": False,
        "sql_error": None,
        "insight": "Insight XYZ",
        "chart_type": "none",
        "forecast_result": [{"period": "T+1", "predicted_value": 100}],
        "forecast_trend": "tăng",
        "anomaly_result": [{"revenue": 999, "z_score": 3.2}],
    }
    result = run_responder_agent(state)
    assert "tăng" in result["final_answer"]
    assert "1" in result["final_answer"]