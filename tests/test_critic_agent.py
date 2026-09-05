from app.agents.critic_agent import run_critic_agent


def test_critic_passes_valid_insight(mock_llm_response, sample_sql_rows):
    with mock_llm_response('{"is_valid": true, "feedback": ""}'):
        state = {"sql_result": sample_sql_rows, "insight": "Electronics cao nhat", "sql_error": None}
        result = run_critic_agent(state)
        assert result["is_valid"] is True


def test_critic_rejects_wrong_insight(mock_llm_response, sample_sql_rows):
    with mock_llm_response('{"is_valid": false, "feedback": "So lieu khong khop"}'):
        state = {"sql_result": sample_sql_rows, "insight": "Books cao nhat", "sql_error": None}
        result = run_critic_agent(state)
        assert result["is_valid"] is False
        assert result["critic_feedback"] != ""


def test_critic_short_circuits_on_sql_error():
    state = {"sql_result": [], "insight": "", "sql_error": "syntax error"}
    result = run_critic_agent(state)
    assert result["is_valid"] is False
    assert "syntax error" in result["critic_feedback"]