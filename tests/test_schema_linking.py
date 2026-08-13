from app.core.schema_linking import get_relevant_examples


def test_returns_k_examples():
    results = get_relevant_examples("Doanh thu theo danh mục", k=3)
    assert len(results) == 3


def test_result_has_sql_field():
    results = get_relevant_examples("Khách hàng ở Hà Nội", k=1)
    assert "sql" in results[0]
    assert "question" in results[0]