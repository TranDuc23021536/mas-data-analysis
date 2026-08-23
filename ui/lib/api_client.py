import os
import requests

API_BASE = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "mas_secret_key_2026")

_HEADERS = {"X-API-Key": API_KEY}


def analyze(question: str, session_id: str | None = None) -> dict:
    payload = {"question": question}
    if session_id:
        payload["session_id"] = session_id
    resp = requests.post(f"{API_BASE}/analyze", json=payload, headers=_HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()


def get_dashboard_summary() -> dict:
    resp = requests.get(f"{API_BASE}/dashboard/summary", headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_products() -> list:
    resp = requests.get(f"{API_BASE}/catalog/products", headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("products", [])


def health() -> bool:
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False