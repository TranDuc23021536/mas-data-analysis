from app.agents.sql_agent import run_sql_agent


def test_sql_agent_generates_and_executes(mock_llm_response):
    sql = "SELECT category_name FROM categories LIMIT 3;"
    with mock_llm_response(sql):
        state = {"question": "Danh sach danh muc", "chat_history": []}
        result = run_sql_agent(state)
        assert result["sql_error"] is None
        assert isinstance(result["sql_result"], list)


def test_sql_agent_blocks_unsafe_query(mock_llm_response):
    with mock_llm_response("DELETE FROM categories;"):
        state = {"question": "Xoa het du lieu", "chat_history": []}
        result = run_sql_agent(state)
        assert result["sql_error"] is not None
        assert result["sql_result"] == []


def test_sql_agent_strips_code_fence(mock_llm_response):
    with mock_llm_response("```sql\nSELECT 1;\n```"):
        state = {"question": "test", "chat_history": []}
        result = run_sql_agent(state)
        assert "```" not in result["sql_query"]