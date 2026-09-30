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


def test_forecast_sorts_out_of_order_time_column():
    state = {
        "needs_forecast": True,
        "sql_result": [
            {"month": "2025-03", "orders": 40, "revenue": 140},
            {"month": "2025-01", "orders": 10, "revenue": 100},
            {"month": "2025-02", "orders": 25, "revenue": 120},
        ],
    }
    result = run_forecast_agent(state)
    assert result["forecast_trend"] == "tăng"
    assert result["forecast_result"][0]["predicted_value"] == 55.0


def test_forecast_without_time_column_falls_back():
    state = {
        "needs_forecast": True,
        "sql_result": [
            {"category": "A", "revenue": 100},
            {"category": "B", "revenue": 120},
            {"category": "C", "revenue": 140},
        ],
    }
    result = run_forecast_agent(state)
    assert result["forecast_result"][0]["period"] == "T+1"


def test_anomaly_skipped_when_not_needed():
    state = {"needs_anomaly": False, "sql_result": []}
    result = run_anomaly_agent(state)
    assert result["anomaly_result"] == []


def test_anomaly_detects_outlier_with_small_sample_via_iqr():
    state = {
        "needs_anomaly": True,
        "sql_result": [
            {"revenue": 100}, {"revenue": 102}, {"revenue": 98},
            {"revenue": 101}, {"revenue": 1000},
        ],
    }
    result = run_anomaly_agent(state)
    assert len(result["anomaly_result"]) >= 1
    assert result["anomaly_result"][0]["revenue"] == 1000


def test_anomaly_no_false_positive_on_uniform_data():
    state = {
        "needs_anomaly": True,
        "sql_result": [{"revenue": 100} for _ in range(6)],
    }
    result = run_anomaly_agent(state)
    assert result["anomaly_result"] == []


def test_anomaly_capped_at_20_results():
    rows = [{"revenue": 100 + (i % 5)} for i in range(80)] + [{"revenue": 9000 + i} for i in range(25)]
    state = {"needs_anomaly": True, "sql_result": rows}
    result = run_anomaly_agent(state)
    assert len(result["anomaly_result"]) == 20