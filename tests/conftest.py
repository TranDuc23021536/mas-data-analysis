import importlib
from contextlib import contextmanager
from unittest.mock import patch

import pytest

_AGENT_MODULES = [
    "planner_agent",
    "sql_agent",
    "analysis_agent",
    "critic_agent",
    "responder_agent",
    "visualization_agent",
]


def _importable(name):
    try:
        importlib.import_module(f"app.agents.{name}")
        return True
    except ImportError:
        return False


@pytest.fixture
def mock_llm_response():
    @contextmanager
    def _mock(response_text):
        patches = [
            patch(f"app.agents.{m}.invoke_with_retry", return_value=response_text, create=True)
            for m in _AGENT_MODULES
            if _importable(m)
        ]
        for p in patches:
            p.start()
        try:
            yield
        finally:
            for p in patches:
                p.stop()

    return _mock


@pytest.fixture
def sample_sql_rows():
    return [
        {"category_name": "Electronics", "revenue": 111.96},
        {"category_name": "Books", "revenue": 76.50},
        {"category_name": "Sports", "revenue": 55.00},
        {"category_name": "Home & Kitchen", "revenue": 25.00},
    ]