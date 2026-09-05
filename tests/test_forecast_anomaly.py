from app.agents.forecast_agent import run_forecast_agent
from app.agents.anomaly_agent import run_anomaly_agent


def test_forecast_skipped_when_not_needed():
    state = {"needs_forecast": False, "sql_result": []}
    result = run_forecast_agent(state)
    assert result["forecast_result"] == []


def test_forecast_returns_trend():
    state = {
        "needs_forecast": True,
        "sql_result": [
            {"month": "2025-01", "revenue": 100},
            {"month": "2025-02", "revenue": 120},
            {"month": "2025-03", "revenue": 140},
        ],
    }
    result = run_forecast_agent(state)
    assert len(result["forecast_result"]) == 3
    assert result["forecast_trend"] == "tăng"


def test_anomaly_skipped_when_not_needed():
    state = {"needs_anomaly": False, "sql_result": []}
    result = run_anomaly_agent(state)
    assert result["anomaly_result"] == []


def test_anomaly_detects_outlier():
    state = {
        "needs_anomaly": True,
        "sql_result": [
            {"revenue": 100}, {"revenue": 102}, {"revenue": 98}, {"revenue": 101},
            {"revenue": 99}, {"revenue": 103}, {"revenue": 97}, {"revenue": 100},
            {"revenue": 1000},
        ],
    }
    result = run_anomaly_agent(state)
    assert len(result["anomaly_result"]) >= 1