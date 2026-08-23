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

def get_dashboard_summary() -> dict:
    tables = ["categories", "products", "customers", "orders", "order_items", "reviews"]
    counts = {}
    for t in tables:
        rows = run_readonly_query(f"SELECT COUNT(*) AS cnt FROM {t};")
        counts[t] = rows[0]["cnt"]

    revenue_rows = run_readonly_query(
        "SELECT COALESCE(SUM(quantity * unit_price), 0) AS total FROM order_items;"
    )
    total_revenue = float(revenue_rows[0]["total"])

    top_category_rows = run_readonly_query("""
        SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_name
        ORDER BY revenue DESC
        LIMIT 1;
    """)
    top_category = top_category_rows[0]["category_name"] if top_category_rows else None

    return {
        "table_counts": counts,
        "total_revenue": total_revenue,
        "top_category": top_category,
    }


def get_product_catalog() -> list:
    return run_readonly_query("""
        SELECT p.product_name, c.category_name, p.price, p.stock_quantity
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_name;
    """)