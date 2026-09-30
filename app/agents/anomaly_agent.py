import numpy as np
from decimal import Decimal
from app.core.state import AgentState

_MAX_ANOMALY_RESULTS = 20
_Z_THRESHOLD = 2.0
_IQR_MULTIPLIER = 1.5


def _detect_anomalies(values: np.ndarray):
    n = len(values)
    mean = values.mean()
    std = values.std()
    z_scores = (values - mean) / std if std > 0 else np.zeros(n)

    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower = q1 - _IQR_MULTIPLIER * iqr
    upper = q3 + _IQR_MULTIPLIER * iqr

    flags = []
    for i in range(n):
        z = float(z_scores[i])
        by_z = abs(z) > _Z_THRESHOLD
        by_iqr = iqr > 0 and (values[i] < lower or values[i] > upper)
        if by_z or by_iqr:
            flags.append((i, z, by_z, by_iqr))
    return flags


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

    flags = _detect_anomalies(values)
    flags.sort(key=lambda f: abs(f[1]), reverse=True)

    anomalies = []
    for i, z, by_z, by_iqr in flags[:_MAX_ANOMALY_RESULTS]:
        method = "z_score+iqr" if (by_z and by_iqr) else ("z_score" if by_z else "iqr")
        anomalies.append({**data[i], "z_score": round(z, 2), "detected_by": method})

    state["anomaly_result"] = anomalies
    return state