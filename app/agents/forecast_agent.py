import re
import numpy as np
from decimal import Decimal
from datetime import date, datetime
from app.core.state import AgentState

_TIME_NAME_HINTS = ("date", "month", "year", "time", "period", "quarter", "week")
_DATE_FORMATS = ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%d/%m/%Y", "%m/%Y")


def _is_time_like_name(name: str) -> bool:
    lower = name.lower()
    return any(hint in lower for hint in _TIME_NAME_HINTS)


def _parse_time_value(value):
    if isinstance(value, (date, datetime)):
        return value
    if isinstance(value, str):
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        if re.fullmatch(r"\d{4}", value):
            return datetime(int(value), 1, 1)
    return None


def _detect_time_column(row: dict):
    for key, value in row.items():
        if _is_time_like_name(key):
            return key
    for key, value in row.items():
        if _parse_time_value(value) is not None:
            return key
    return None


def _to_numeric(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    return None


def _sort_key(row, time_col):
    if time_col is None:
        return 0
    parsed = _parse_time_value(row.get(time_col))
    return parsed if parsed is not None else datetime.min


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

    time_col = _detect_time_column(data[0])
    if time_col:
        data = sorted(data, key=lambda r: _sort_key(r, time_col))

    numeric_cols = [
        k for k, v in data[0].items()
        if _to_numeric(v) is not None and k != time_col
    ]

    if not numeric_cols:
        state["forecast_result"] = []
        return state

    target_col = numeric_cols[0]
    values = [_to_numeric(row[target_col]) for row in data]

    forecast, slope = _linear_forecast(values)

    next_labels = [f"T+{i+1}" for i in range(len(forecast))]
    if time_col:
        last_value = data[-1].get(time_col)
        next_labels = [f"Sau {last_value} (+{i+1})" for i in range(len(forecast))]

    state["forecast_result"] = [
        {"period": label, "predicted_value": round(v, 2)}
        for label, v in zip(next_labels, forecast)
    ]
    state["forecast_trend"] = "tăng" if slope > 0 else "giảm" if slope < 0 else "ổn định"

    return state