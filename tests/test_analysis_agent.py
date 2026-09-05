from app.agents.analysis_agent import run_analysis_agent


def test_analysis_returns_insight(mock_llm_response, sample_sql_rows):
    with mock_llm_response("Electronics dat doanh thu cao nhat."):
        state = {"question": "test", "sql_result": sample_sql_rows}
        result = run_analysis_agent(state)
        assert result["insight"] != ""


def test_analysis_handles_empty_data(mock_llm_response):
    with mock_llm_response("Khong co du lieu phu hop."):
        state = {"question": "test", "sql_result": []}
        result = run_analysis_agent(state)
        assert "khong" in result["insight"].lower() or "không" in result["insight"].lower()