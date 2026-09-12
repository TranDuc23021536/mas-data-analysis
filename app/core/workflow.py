from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.planner_agent import run_planner
from app.agents.sql_agent import run_sql_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.visualization_agent import run_visualization_agent
from app.agents.forecast_agent import run_forecast_agent
from app.agents.anomaly_agent import run_anomaly_agent
from app.agents.critic_agent import run_critic_agent
from app.agents.responder_agent import run_responder_agent

MAX_RETRIES = 2


def _route_after_planner(state: AgentState) -> str:
    if state.get("is_smalltalk"):
        return "responder"
    if state.get("chart_only"):
        return "visualization"
    return "sql"


def _route_after_visualization(state: AgentState) -> str:
    if state.get("chart_only"):
        return "responder"
    return "forecast"


def _route_after_critic(state: AgentState) -> str:
    if state.get("is_valid"):
        return "responder"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "responder"
    return "retry"


def _increment_retry(state: AgentState) -> AgentState:
    state["retry_count"] = state.get("retry_count", 0) + 1
    return state


def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("planner", run_planner)
    graph.add_node("sql", run_sql_agent)
    graph.add_node("analysis", run_analysis_agent)
    graph.add_node("visualization", run_visualization_agent)
    graph.add_node("forecast", run_forecast_agent)
    graph.add_node("anomaly", run_anomaly_agent)
    graph.add_node("critic", run_critic_agent)
    graph.add_node("retry", _increment_retry)
    graph.add_node("responder", run_responder_agent)

    graph.set_entry_point("planner")

    graph.add_conditional_edges("planner", _route_after_planner, {
        "sql": "sql",
        "visualization": "visualization",
        "responder": "responder",
    })

    graph.add_edge("sql", "analysis")
    graph.add_edge("analysis", "visualization")

    graph.add_conditional_edges("visualization", _route_after_visualization, {
        "forecast": "forecast",
        "responder": "responder",
    })

    graph.add_edge("forecast", "anomaly")
    graph.add_edge("anomaly", "critic")

    graph.add_conditional_edges("critic", _route_after_critic, {
        "retry": "retry",
        "responder": "responder",
    })

    graph.add_edge("retry", "sql")
    graph.add_edge("responder", END)

    return graph.compile()


workflow = build_workflow()