from unittest.mock import patch

from app.agents.critic_agent import run_critic_agent


def test_critic_short_circuits_on_sql_error():
    state = {"sql_result": [], "insight": "", "sql_error": "syntax error"}
    result = run_critic_agent(state)
    assert result["approved"] is False
    assert result["is_valid"] is False
    assert result["target_agent"] == "sql"
    assert "syntax error" in result["critic_feedback"]


def test_critic_layer1_rejects_wrong_number_without_calling_llm(sample_sql_rows):
    state = {"sql_result": sample_sql_rows, "insight": "Electronics đạt 120,50 USD.", "sql_error": None}
    with patch("app.agents.critic_agent.invoke_with_retry") as llm:
        result = run_critic_agent(state)
        llm.assert_not_called()
    assert result["approved"] is False
    assert result["target_agent"] == "analysis"
    assert result["fact_check_issues"] == ["120,50"]


def test_critic_approves_when_numbers_and_llm_ok(mock_llm_response, sample_sql_rows):
    state = {"sql_result": sample_sql_rows, "insight": "Electronics dẫn đầu với 111,96 USD.", "sql_error": None}
    with mock_llm_response('{"approved": true, "feedback": "", "target_agent": ""}'):
        result = run_critic_agent(state)
    assert result["approved"] is True
    assert result["is_valid"] is True
    assert result["fact_check_issues"] == []


def test_critic_llm_rejection_routes_to_sql(mock_llm_response, sample_sql_rows):
    state = {"sql_result": sample_sql_rows, "insight": "Electronics dẫn đầu với 111,96 USD.", "sql_error": None}
    with mock_llm_response('{"approved": false, "feedback": "SQL sai bảng", "target_agent": "sql"}'):
        result = run_critic_agent(state)
    assert result["approved"] is False
    assert result["target_agent"] == "sql"
    assert result["critic_feedback"] == "SQL sai bảng"


def test_critic_invalid_target_defaults_to_analysis(mock_llm_response, sample_sql_rows):
    state = {"sql_result": sample_sql_rows, "insight": "Electronics dẫn đầu.", "sql_error": None}
    with mock_llm_response('{"approved": false, "feedback": "sai", "target_agent": "visualization"}'):
        result = run_critic_agent(state)
    assert result["target_agent"] == "analysis"


def test_critic_invalid_json_fails_open(mock_llm_response, sample_sql_rows):
    state = {"sql_result": sample_sql_rows, "insight": "Electronics dẫn đầu.", "sql_error": None}
    with mock_llm_response("không phải json"):
        result = run_critic_agent(state)
    assert result["approved"] is True