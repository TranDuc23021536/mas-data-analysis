import numpy as np
from app.core.state import AgentState


def _linear_forecast(values: list, periods_ahead: int = 3):
    x = np.arange(len(values))
    y = np.array(values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)

    future_x = np.arange(len(values), len(values) + periods_ahead)
    forecast = (slope * future_x + intercept).tolist()
    return forecast, slope


def run_forecast_agent(state: AgentState) -> AgentState:
    if not state.get("needs_forecast"):
        state["forecast_result"] = []
        return state

    data = state.get("sql_result", [])
    if len(data) < 2:
        state["forecast_result"] = []
        return state

    numeric_cols = [k for k, v in data[0].items() if isinstance(v, (int, float))]
    from decimal import Decimal
    numeric_cols += [k for k, v in data[0].items() if isinstance(v, Decimal)]

    if not numeric_cols:
        state["forecast_result"] = []
        return state

    target_col = numeric_cols[0]
    values = [float(row[target_col]) for row in data]

    forecast, slope = _linear_forecast(values)

    state["forecast_result"] = [
        {"period": f"T+{i+1}", "predicted_value": round(v, 2)}
        for i, v in enumerate(forecast)
    ]
    state["forecast_trend"] = "tăng" if slope > 0 else "giảm" if slope < 0 else "ổn định"

    return state