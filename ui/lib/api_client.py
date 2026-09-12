import os
import requests
import json

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
    
def upload_file(file_bytes: bytes, filename: str) -> dict:
    files = {"file": (filename, file_bytes)}
    resp = requests.post(f"{API_BASE}/upload/csv", files=files, headers=_HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()


def list_uploaded_tables() -> list:
    resp = requests.get(f"{API_BASE}/upload/tables", headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("tables", [])

def analyze_stream(question: str, session_id: str | None = None):
    payload = {"question": question}
    if session_id:
        payload["session_id"] = session_id

    with requests.post(
        f"{API_BASE}/analyze/stream",
        json=payload,
        headers=_HEADERS,
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        event_type = None
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            if raw_line.startswith("event:"):
                event_type = raw_line.split(":", 1)[1].strip()
            elif raw_line.startswith("data:"):
                data_str = raw_line.split(":", 1)[1].strip()
                data = json.loads(data_str)
                yield event_type, data