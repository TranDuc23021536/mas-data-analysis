import pytest
from app.db.database import run_readonly_query, UnsafeQueryError


def test_select_query_works():
    result = run_readonly_query("SELECT * FROM categories LIMIT 1;")
    assert isinstance(result, list)


def test_delete_query_blocked():
    with pytest.raises(UnsafeQueryError):
        run_readonly_query("DELETE FROM categories;")


def test_drop_query_blocked():
    with pytest.raises(UnsafeQueryError):
        run_readonly_query("DROP TABLE categories;")


def test_non_select_start_blocked():
    with pytest.raises(UnsafeQueryError):
        run_readonly_query("UPDATE categories SET category_name = 'x';")