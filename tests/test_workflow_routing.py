from app.core.workflow import _route_after_planner, _route_after_critic, MAX_RETRIES


def test_route_smalltalk_goes_to_responder():
    state = {"is_smalltalk": True}
    assert _route_after_planner(state) == "responder"


def test_route_data_question_goes_to_sql():
    state = {"is_smalltalk": False}
    assert _route_after_planner(state) == "sql"


def test_route_valid_critic_goes_to_responder():
    state = {"is_valid": True, "retry_count": 0}
    assert _route_after_critic(state) == "responder"


def test_route_invalid_critic_retries():
    state = {"is_valid": False, "retry_count": 0}
    assert _route_after_critic(state) == "retry"


def test_route_max_retries_gives_up():
    state = {"is_valid": False, "retry_count": MAX_RETRIES}
    assert _route_after_critic(state) == "responder"