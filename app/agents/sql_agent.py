import re
import logging
from app.core.state import AgentState
from app.core.schema_linking import get_relevant_examples, format_examples_for_prompt
from app.core.llm import invoke_with_retry, strip_code_fence
from app.db.database import run_readonly_query, get_schema_description, UnsafeQueryError

logger = logging.getLogger("mas.sql_agent")

_SYSTEM_PROMPT = """Bạn là SQL Agent. Nhiệm vụ: dựa trên schema cơ sở dữ liệu và các ví dụ mẫu, sinh ra một câu lệnh SQL PostgreSQL duy nhất để trả lời câu hỏi.

QUAN TRỌNG: Nếu câu hỏi hỏi về CẤU TRÚC dữ liệu (có những bảng nào, bảng nào có cột gì, tổng quan schema), KHÔNG được tự bịa tên bảng. Phải dùng truy vấn vào information_schema, ví dụ:
- Liệt kê bảng: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
- Liệt kê cột của 1 bảng: SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '<ten_bang>'

Chỉ dùng các bảng CÓ THẬT được liệt kê trong schema dưới đây. Không tự bịa tên bảng dựa theo từ khóa trong câu hỏi (ví dụ "doanh thu" không phải tên bảng, mà là giá trị tính từ order_items.quantity * order_items.unit_price).

Schema cơ sở dữ liệu:
{schema}

Các ví dụ tham khảo:
{examples}

Chỉ trả về câu lệnh SQL, không giải thích, không dùng markdown, không có dấu chấm phẩy thừa."""


def _extract_table_name(sql: str) -> str | None:
    match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
    return match.group(1) if match else None


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

    # Chỉ cập nhật active_table nếu query chạy thành công, tránh nhiễm bảng bịa khi lỗi
    if state["sql_error"] is None:
        extracted_table = _extract_table_name(sql)
        if extracted_table:
            state["active_table"] = extracted_table

    return state