import os
import json
import psycopg2
import psycopg2.extras
from typing import Any

FORBIDDEN_FIELDS: frozenset[str] = frozenset({
    "face_embedding", "face_embedding_encrypted",
    "raw_face_image", "raw_face_image_path",
    "biometric_vector", "biometric_data",
    "embedding_blob", "face_crop", "facial_features",
})


def _get_conn():
    url = os.environ.get("DATABASE_URL", "postgresql://localhost/nonconsent_detection")
    return psycopg2.connect(url)


def _strip_forbidden(row: dict) -> dict:
    return {k: v for k, v in row.items() if k not in FORBIDDEN_FIELDS}


def get_cases(
    status: str | None = None,
    risk_level: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    filters, params = [], []
    if status:
        filters.append("status = %s"); params.append(status)
    if risk_level:
        filters.append("risk_level = %s"); params.append(risk_level)
    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    params += [limit, offset]
    sql = f"SELECT * FROM detection_cases {where} ORDER BY created_at DESC LIMIT %s OFFSET %s"
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    return [_strip_forbidden(dict(r)) for r in rows]


def get_case_by_id(case_id: str) -> dict | None:
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM detection_cases WHERE case_id = %s", (case_id,))
            row = cur.fetchone()
    return _strip_forbidden(dict(row)) if row else None


def get_case_stats() -> dict:
    sql = """
        SELECT
            COUNT(*)                                        AS total,
            COUNT(*) FILTER (WHERE status='pending')       AS pending,
            COUNT(*) FILTER (WHERE status='approved')      AS approved,
            COUNT(*) FILTER (WHERE status='rejected')      AS rejected,
            COUNT(*) FILTER (WHERE status='error')         AS error,
            COUNT(*) FILTER (WHERE risk_level='high')      AS high_risk,
            COUNT(*) FILTER (WHERE risk_level='medium')    AS medium_risk,
            COUNT(*) FILTER (WHERE risk_level='low')       AS low_risk,
            COUNT(*) FILTER (WHERE manual_review_required) AS needs_review
        FROM detection_cases
    """
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            row = cur.fetchone()
    return dict(row) if row else {}


def get_audit_logs(
    case_id: str | None = None,
    action_type: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict]:
    filters, params = [], []
    if case_id:
        filters.append("case_id = %s"); params.append(case_id)
    if action_type:
        filters.append("action_type = %s"); params.append(action_type)
    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    params += [limit, offset]
    sql = f"SELECT * FROM audit_logs {where} ORDER BY created_at DESC LIMIT %s OFFSET %s"
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def load_evidence_report(report_path: str) -> dict | None:
    reports_dir = os.environ.get("REPORTS_DIR", "reports")
    full_path   = os.path.join(reports_dir, os.path.basename(report_path))
    if not os.path.isfile(full_path):
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if k not in FORBIDDEN_FIELDS}