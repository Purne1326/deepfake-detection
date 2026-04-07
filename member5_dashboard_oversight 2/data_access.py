import sqlite3
import os
import json
from datetime import datetime

# Path to the main audit database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audit.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_case_stats():
    conn = get_db_connection()
    # In our simplified schema, we derive stats from audit_logs action_type
    try:
        total = conn.execute("SELECT COUNT(distinct post_id) FROM audit_logs").fetchone()[0] or 0
        pending = conn.execute("SELECT COUNT(*) FROM audit_logs WHERE action_type='DETECTION_RECEIVED'").fetchone()[0] or 0
        approved = conn.execute("SELECT COUNT(*) FROM audit_logs WHERE action_type='TAKEDOWN_REQUESTED'").fetchone()[0] or 0
        # Mocking some stats since we only have audit logs for now
        return {
            "total": total,
            "pending": pending if pending > approved else 0,
            "approved": approved,
            "rejected": 0,
            "error": 0,
            "high_risk": total,
            "medium_risk": 0,
            "low_risk": 0,
            "needs_review": pending if pending > approved else 0
        }
    finally:
        conn.close()

def get_cases(status=None, risk_level=None, limit=50):
    conn = get_db_connection()
    try:
        # We find distinct post_ids and their latest audit log
        rows = conn.execute("""
            SELECT post_id, platform, url, action_type, timestamp, details 
            FROM audit_logs 
            GROUP BY post_id 
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        cases = []
        for r in rows:
            details = json.loads(r['details']) if r['details'] else {}
            cases.append({
                "case_id": f"CASE-{r['post_id']}",
                "platform": r['platform'],
                "post_id": r['post_id'],
                "post_url": r['url'] or details.get("url", ""),
                "status": "approved" if r['action_type'] == "TAKEDOWN_REQUESTED" else "pending",
                "risk_level": details.get("overall_risk_level", "medium"),
                "match_confidence": details.get("confidence", 0.9),
                "deepfake_score": details.get("deepfake", {}).get("score", 0.0),
                "nudity_score": details.get("nudity", {}).get("score", 0.0),
                "created_at": r['timestamp'],
                "updated_at": r['timestamp']
            })
        return cases
    finally:
        conn.close()

def get_case_by_id(case_id):
    post_id = case_id.replace("CASE-", "")
    cases = get_cases(limit=1000)
    for c in cases:
        if c["post_id"] == post_id:
            return c
    return None

def get_audit_logs(case_id=None, limit=100):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM audit_logs"
        params = []
        if case_id:
            query += " WHERE post_id = ?"
            params.append(case_id.replace("CASE-", ""))
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def load_evidence_report(path):
    # If the path is relative, try to find it in the reports dir
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "member4_automation_compliance", "reports"))
    full_path = os.path.join(reports_dir, os.path.basename(path))
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return json.load(f)
    return None
