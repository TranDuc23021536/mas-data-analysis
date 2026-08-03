from app.core.state import AgentState
from app.agents.planner_agent import run_planner

state: AgentState = {
    "question": "Chào bạn",
    "chat_history": [],
}

result = run_planner(state)
print(result)