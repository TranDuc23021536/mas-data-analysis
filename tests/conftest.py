import pytest
from unittest.mock import patch


@pytest.fixture
def mock_llm_response():
    """Fixture cho phép giả lập phản hồi LLM mà không gọi API thật."""
    def _mock(response_text: str):
        return patch("app.core.llm.invoke_with_retry", return_value=response_text)
    return _mock


@pytest.fixture
def sample_sql_rows():
    return [
        {"category_name": "Electronics", "revenue": 111.96},
        {"category_name": "Books", "revenue": 76.50},
        {"category_name": "Sports", "revenue": 55.00},
        {"category_name": "Home & Kitchen", "revenue": 25.00},
    ]