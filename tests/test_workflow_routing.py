from app.core.workflow import (
    _route_after_planner,
    _route_after_visualization,
    _route_after_critic,
    _route_after_retry,
    MAX_RETRIES,
)


def test_route_smalltalk_goes_to_responder():
    assert _route_after_planner({"is_smalltalk": True}) == "responder"


def test_route_data_question_goes_to_sql():
    assert _route_after_planner({"is_smalltalk": False, "chart_only": False}) == "sql"


def test_route_chart_only_goes_to_visualization():
    assert _route_after_planner({"is_smalltalk": False, "chart_only": True}) == "visualization"


def test_route_after_visualization_chart_only_goes_to_responder():
    assert _route_after_visualization({"chart_only": True}) == "responder"


def test_route_after_visualization_normal_goes_to_forecast():
    assert _route_after_visualization({"chart_only": False}) == "forecast"


def test_route_valid_critic_goes_to_responder():
    assert _route_after_critic({"approved": True, "retry_count": 0}) == "responder"


def test_route_invalid_critic_retries():
    assert _route_after_critic({"approved": False, "retry_count": 0}) == "retry"


def test_route_max_retries_gives_up():
    assert _route_after_critic({"approved": False, "retry_count": MAX_RETRIES}) == "responder"


def test_route_after_retry_goes_to_analysis():
    assert _route_after_retry({"target_agent": "analysis"}) == "analysis"


def test_route_after_retry_defaults_to_sql():
    assert _route_after_retry({"target_agent": "sql"}) == "sql"
    assert _route_after_retry({}) == "sql"