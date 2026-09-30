from unittest.mock import patch

from app.agents.visualization_agent import run_visualization_agent


def test_not_needed_returns_none():
    state = {"needs_chart": False, "chart_only": False, "sql_result": [{"a": 1}]}
    result = run_visualization_agent(state)
    assert result["chart_type"] == "none"
    assert result["chart_data"] == []


def test_empty_data_returns_none():
    state = {"needs_chart": True, "sql_result": []}
    result = run_visualization_agent(state)
    assert result["chart_type"] == "none"


def test_llm_valid_proposal_is_used(sample_sql_rows):
    with patch(
        "app.agents.visualization_agent.invoke_with_retry",
        return_value='{"chart_type":"pie","x_col":"category_name","y_col":"revenue"}',
    ):
        state = {"needs_chart": True, "sql_result": sample_sql_rows, "question": "tỷ trọng doanh thu"}
        result = run_visualization_agent(state)
    assert result["chart_type"] == "pie"
    assert result["chart_data"][0] == {"category_name": "Electronics", "revenue": 111.96}


def test_llm_invalid_column_falls_back_to_rule_based(sample_sql_rows):
    with patch(
        "app.agents.visualization_agent.invoke_with_retry",
        return_value='{"chart_type":"bar","x_col":"nonexistent","y_col":"revenue"}',
    ):
        state = {"needs_chart": True, "sql_result": sample_sql_rows, "question": "doanh thu theo danh mục"}
        result = run_visualization_agent(state)
    assert result["chart_type"] == "bar"
    assert set(result["chart_data"][0].keys()) == {"category_name", "revenue"}


def test_llm_non_numeric_y_falls_back(sample_sql_rows):
    with patch(
        "app.agents.visualization_agent.invoke_with_retry",
        return_value='{"chart_type":"bar","x_col":"revenue","y_col":"category_name"}',
    ):
        state = {"needs_chart": True, "sql_result": sample_sql_rows, "question": "doanh thu theo danh mục"}
        result = run_visualization_agent(state)
    assert result["chart_type"] == "bar"


def test_llm_failure_falls_back_to_rule_based(sample_sql_rows):
    with patch("app.agents.visualization_agent.invoke_with_retry", side_effect=RuntimeError("timeout")):
        state = {"needs_chart": True, "sql_result": sample_sql_rows, "question": "doanh thu theo danh mục"}
        result = run_visualization_agent(state)
    assert result["chart_type"] == "bar"


def test_chart_only_override_skips_llm(sample_sql_rows):
    with patch("app.agents.visualization_agent.invoke_with_retry") as llm:
        state = {"chart_only": True, "requested_chart_type": "pie", "sql_result": sample_sql_rows}
        result = run_visualization_agent(state)
        llm.assert_not_called()
    assert result["chart_type"] == "pie"


def test_scatter_for_two_numeric_columns():
    data = [{"price": 10, "rating": 4.5}, {"price": 20, "rating": 4.2}, {"price": 15, "rating": 4.8}]
    with patch(
        "app.agents.visualization_agent.invoke_with_retry",
        return_value='{"chart_type":"scatter","x_col":"price","y_col":"rating"}',
    ):
        state = {"needs_chart": True, "sql_result": data, "question": "quan hệ giá và đánh giá"}
        result = run_visualization_agent(state)
    assert result["chart_type"] == "scatter"