import logging
from app.core.state import AgentState
from app.core.schema_linking import get_relevant_examples, format_examples_for_prompt
from app.core.llm import invoke_with_retry, strip_code_fence
from app.db.database import run_readonly_query, get_schema_description, UnsafeQueryError

logger = logging.getLogger("mas.sql_agent")

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

    logger.info(f"Generating SQL for: {question[:80]}")

    sql = invoke_with_retry([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ])
    sql = strip_code_fence(sql, lang_hint="sql")

    state["sql_query"] = sql

    try:
        state["sql_result"] = run_readonly_query(sql)
        state["sql_error"] = None
        logger.info(f"SQL executed successfully, {len(state['sql_result'])} rows returned")
    except UnsafeQueryError as e:
        logger.warning(f"Unsafe query blocked: {e}")
        state["sql_result"] = []
        state["sql_error"] = str(e)
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        state["sql_result"] = []
        state["sql_error"] = str(e)

    return state