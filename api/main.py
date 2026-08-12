from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.workflow import workflow

app = FastAPI(title="MAS Data Analysis API")


class AnalyzeRequest(BaseModel):
    question: str
    chat_history: list = []


class AnalyzeResponse(BaseModel):
    final_answer: str
    sql_query: str = ""
    chart_type: str = "none"
    chart_data: list = []
    is_valid: bool = True


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        result = workflow.invoke({
            "question": req.question,
            "chat_history": req.chat_history,
            "retry_count": 0,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AnalyzeResponse(
        final_answer=result.get("final_answer", ""),
        sql_query=result.get("sql_query", ""),
        chart_type=result.get("chart_type", "none"),
        chart_data=result.get("chart_data", []),
        is_valid=result.get("is_valid", True),
    )


@app.get("/health")
def health():
    return {"status": "ok"}