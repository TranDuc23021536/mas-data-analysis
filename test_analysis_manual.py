from app.core.state import AgentState
from app.agents.planner_agent import run_planner
from app.agents.sql_agent import run_sql_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.visualization_agent import run_visualization_agent

state: AgentState = {
    "question": "Doanh thu theo từng danh mục sản phẩm là bao nhiêu?",
    "chat_history": [],
}

state = run_planner(state)
state = run_sql_agent(state)
state = run_analysis_agent(state)
state = run_visualization_agent(state)

print("Insight:", state["insight"])
print("Chart type:", state["chart_type"])
print("Chart data:", state["chart_data"])