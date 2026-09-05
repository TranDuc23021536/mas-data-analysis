import json
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.workflow import workflow
from app.db.database import get_dashboard_summary, get_product_catalog

from app.core.config import settings
_API_KEY = settings.API_KEY


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not _API_KEY:
        return
    if x_api_key != _API_KEY:
        raise HTTPException(status_code=401, detail="API key không hợp lệ hoặc thiếu (header X-API-Key).")


_SESSION_STORE: dict[str, list[dict]] = {}
_MAX_HISTORY_PER_SESSION = 20


def _get_session_history(session_id: str) -> list[dict]:
    return _SESSION_STORE.get(session_id, [])


def _append_session_turn(session_id: str, question: str, answer: str) -> None:
    turns = _SESSION_STORE.setdefault(session_id, [])
    turns.append({"role": "user", "content": question})
    turns.append({"role": "assistant", "content": answer})
    if len(turns) > _MAX_HISTORY_PER_SESSION:
        del turns[: len(turns) - _MAX_HISTORY_PER_SESSION]


app = FastAPI(title="MAS Data Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    question: str
    session_id: str | None = None


class AnalyzeResponse(BaseModel):
    session_id: str
    final_answer: str
    sql_query: str = ""
    chart_type: str = "none"
    chart_data: list = []
    forecast_result: list = []
    anomaly_result: list = []
    is_valid: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


def _run_pipeline(question: str, session_id: str) -> dict:
    chat_history = _get_session_history(session_id)
    result = workflow.invoke({
        "question": question,
        "chat_history": chat_history,
        "retry_count": 0,
    })
    _append_session_turn(session_id, question, result.get("final_answer", ""))
    return result


@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_api_key)])
def analyze(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")

    session_id = req.session_id or str(uuid.uuid4())

    try:
        result = _run_pipeline(req.question, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AnalyzeResponse(
        session_id=session_id,
        final_answer=result.get("final_answer", ""),
        sql_query=result.get("sql_query", ""),
        chart_type=result.get("chart_type", "none"),
        chart_data=result.get("chart_data", []),
        forecast_result=result.get("forecast_result", []),
        anomaly_result=result.get("anomaly_result", []),
        is_valid=result.get("is_valid", True),
    )


_NODE_LABELS_VI = {
    "planner": "Planner Agent đang lập kế hoạch...",
    "sql": "SQL Agent đang truy vấn dữ liệu...",
    "analysis": "Analysis Agent đang phân tích...",
    "visualization": "Visualization Agent đang chọn biểu đồ...",
    "forecast": "Forecast Agent đang dự báo...",
    "anomaly": "Anomaly Agent đang tìm bất thường...",
    "critic": "Critic Agent đang kiểm tra chéo...",
    "responder": "Đang tổng hợp câu trả lời...",
}


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


@app.post("/analyze/stream", dependencies=[Depends(require_api_key)])
def analyze_stream(req: AnalyzeRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")

    session_id = req.session_id or str(uuid.uuid4())
    chat_history = _get_session_history(session_id)

    def event_generator():
        initial_state = {"question": req.question, "chat_history": chat_history, "retry_count": 0}
        last_state = dict(initial_state)
        try:
            for update in workflow.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in update.items():
                    last_state.update(node_output)
                    label = _NODE_LABELS_VI.get(node_name, f"Đang chạy {node_name}...")
                    yield _sse_event("progress", {"node": node_name, "label": label})
        except Exception as e:
            yield _sse_event("error", {"detail": str(e)})
            return

        _append_session_turn(session_id, req.question, last_state.get("final_answer", ""))

        final_payload = {
            "session_id": session_id,
            "final_answer": last_state.get("final_answer", ""),
            "sql_query": last_state.get("sql_query", ""),
            "chart_type": last_state.get("chart_type", "none"),
            "chart_data": last_state.get("chart_data", []),
            "forecast_result": last_state.get("forecast_result", []),
            "anomaly_result": last_state.get("anomaly_result", []),
        }
        yield _sse_event("final", final_payload)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/sessions/{session_id}/history", dependencies=[Depends(require_api_key)])
def get_session_history(session_id: str):
    return {"session_id": session_id, "history": _get_session_history(session_id)}


@app.delete("/sessions/{session_id}", dependencies=[Depends(require_api_key)])
def delete_session(session_id: str):
    _SESSION_STORE.pop(session_id, None)
    return {"session_id": session_id, "deleted": True}

@app.get("/dashboard/summary", dependencies=[Depends(require_api_key)])
def dashboard_summary():
    try:
        return get_dashboard_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/catalog/products", dependencies=[Depends(require_api_key)])
def catalog_products():
    try:
        return {"products": get_product_catalog()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))