import re
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

_ALLOWED_START = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


class UnsafeQueryError(Exception):
    pass


def run_readonly_query(sql: str, limit: int = 200):
    if not _ALLOWED_START.match(sql):
        raise UnsafeQueryError("Chỉ cho phép câu lệnh SELECT hoặc WITH.")
    if _FORBIDDEN_KEYWORDS.search(sql):
        raise UnsafeQueryError("Câu lệnh chứa từ khóa không được phép.")

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(row._mapping) for row in result.fetchmany(limit)]
    return rows


def get_schema_description() -> str:
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    rows = run_readonly_query(query)
    schema: dict[str, list[str]] = {}
    for r in rows:
        schema.setdefault(r["table_name"], []).append(f"{r['column_name']} ({r['data_type']})")

    lines = []
    for table, cols in schema.items():
        lines.append(f"- {table}: " + ", ".join(cols))
    return "\n".join(lines)