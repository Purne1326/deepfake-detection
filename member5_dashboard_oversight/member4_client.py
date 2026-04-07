import os
import requests
from typing import Any


def _base_url() -> str:
    return os.environ.get("MEMBER4_BASE_URL", "http://localhost:8004").rstrip("/")


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    api_key = os.environ.get("MEMBER4_API_KEY", "")
    if api_key:
        h["X-API-Key"] = api_key
    return h


def _post(path: str, payload: dict) -> dict[str, Any]:
    try:
        r = requests.post(f"{_base_url()}{path}", json=payload,
                          headers=_headers(), timeout=10)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def approve_case(case_id: str, reviewer: str, notes: str = "") -> dict[str, Any]:
    return _post("/internal/manual-approve",
                 {"case_id": case_id, "reviewer": reviewer, "notes": notes})


def reject_case(case_id: str, reviewer: str, reason: str = "") -> dict[str, Any]:
    return _post("/internal/manual-reject",
                 {"case_id": case_id, "reviewer": reviewer, "reason": reason})


def retry_case(case_id: str, reviewer: str) -> dict[str, Any]:
    return _post("/internal/retry",
                 {"case_id": case_id, "requested_by": reviewer})


def health_check() -> dict[str, Any]:
    try:
        r = requests.get(f"{_base_url()}/health", headers=_headers(), timeout=5)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Health check timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}