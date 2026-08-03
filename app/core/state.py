from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    question: str
    chat_history: List[Dict[str, str]]

    is_smalltalk: bool
    rewritten_question: str
    needs_chart: bool
    needs_forecast: bool
    needs_anomaly: bool

    sql_query: str
    sql_result: List[Dict[str, Any]]
    sql_error: Optional[str]

    insight: str

    is_valid: bool
    critic_feedback: str
    retry_count: int
    
    chart_type: str
    chart_data: List[Dict[str, Any]]

    final_answer: str