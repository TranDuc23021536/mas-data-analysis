from app.core.workflow import workflow


def test_workflow_returns_final_answer():
    result = workflow.invoke({
        "question": "Doanh thu theo từng danh mục sản phẩm là bao nhiêu?",
        "chat_history": [],
        "retry_count": 0,
    })
    assert result["final_answer"] != ""
    assert result["sql_error"] is None


def test_workflow_smalltalk_skips_sql():
    result = workflow.invoke({
        "question": "Chào bạn",
        "chat_history": [],
        "retry_count": 0,
    })
    assert result["is_smalltalk"] is True
    assert result.get("sql_query", "") == ""