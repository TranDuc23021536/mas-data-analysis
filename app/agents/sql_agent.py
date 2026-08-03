import json
from langchain_groq import ChatGroq
from app.core.config import settings
from app.core.state import AgentState
from app.core.schema_linking import get_relevant_examples, format_examples_for_prompt
from app.db.database import run_readonly_query, get_schema_description, UnsafeQueryError

_llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0)

_SYSTEM_PROMPT = """Bạn là SQL Agent. Nhiệm vụ: dựa trên schema cơ sở dữ liệu và các ví dụ mẫu, sinh ra một câu lệnh SQL PostgreSQL duy nhất để trả lời câu hỏi.

Schema cơ sở dữ liệu:
{schema}

Các ví dụ tham khảo:
{examples}

Chỉ trả về câu lệnh SQL, không giải thích, không dùng markdown, không có dấu chấm phẩy thừa."""


def run_sql_agent(state: AgentState) -> AgentState:
    question = state.get("rewritten_question") or state["question"]

    schema = get_schema_description()
    examples = format_examples_for_prompt(get_relevant_examples(question))

    system_prompt = _SYSTEM_PROMPT.format(schema=schema, examples=examples)

    response = _llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ])

    sql = response.content.strip()
    if sql.startswith("```"):
        sql = sql.strip("`").replace("sql", "", 1).strip()

    state["sql_query"] = sql

    try:
        state["sql_result"] = run_readonly_query(sql)
        state["sql_error"] = None
    except UnsafeQueryError as e:
        state["sql_result"] = []
        state["sql_error"] = str(e)
    except Exception as e:
        state["sql_result"] = []
        state["sql_error"] = str(e)

    return state