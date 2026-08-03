from app.core.state import AgentState
from app.agents.planner_agent import run_planner
from app.agents.sql_agent import run_sql_agent

state: AgentState = {
    "question": "Doanh thu theo từng danh mục sản phẩm là bao nhiêu?",
    "chat_history": [],
}

state = run_planner(state)
state = run_sql_agent(state)

print("SQL:", state["sql_query"])
print("Error:", state["sql_error"])
print("Result:", state["sql_result"])