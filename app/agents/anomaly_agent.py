import numpy as np
from decimal import Decimal
from app.core.state import AgentState


def run_anomaly_agent(state: AgentState) -> AgentState:
    if not state.get("needs_anomaly"):
        state["anomaly_result"] = []
        return state

    data = state.get("sql_result", [])
    if len(data) < 4:
        state["anomaly_result"] = []
        return state

    numeric_cols = [k for k, v in data[0].items() if isinstance(v, (int, float, Decimal))]
    if not numeric_cols:
        state["anomaly_result"] = []
        return state

    target_col = numeric_cols[0]
    values = np.array([float(row[target_col]) for row in data])

    mean = values.mean()
    std = values.std()

    anomalies = []
    if std > 0:
        z_scores = (values - mean) / std
        for i, z in enumerate(z_scores):
            if abs(z) > 2:
                anomalies.append({**data[i], "z_score": round(float(z), 2)})

    state["anomaly_result"] = anomalies
    return state