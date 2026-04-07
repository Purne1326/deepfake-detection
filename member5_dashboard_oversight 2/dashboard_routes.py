from __future__ import annotations
import json
from datetime import datetime, timedelta
import random
import pandas as pd
import streamlit as st
from access_control import can, require
from data_access import (
    get_case_stats, get_cases, get_case_by_id,
    get_audit_logs, load_evidence_report,
)
from member4_client import approve_case, reject_case, retry_case, health_check

# ── Demo data ──────────────────────────────────────────────────────────────────
_STATUSES  = ["pending", "approved", "rejected", "error"]
_RISKS     = ["high", "medium", "low"]
_PLATFORMS = ["dummy_social", "Instagram", "X", "Facebook"]

def _demo_cases(n: int = 30) -> list[dict]:
    random.seed(42)
    cases = []
    for i in range(n):
        cases.append({
            "case_id": f"CASE-{1000+i}", "platform": random.choice(_PLATFORMS),
            "post_id": f"post_{i:04d}", "post_url": f"https://example.com/post/{i}",
            "status": random.choice(_STATUSES), "risk_level": random.choice(_RISKS),
            "match_confidence": round(random.uniform(0.5,1.0),3),
            "match_distance":   round(random.uniform(0.0,0.5),3),
            "deepfake_score":   round(random.uniform(0.0,1.0),3),
            "nudity_score":     round(random.uniform(0.0,1.0),3),
            "compliance_reason": "threshold_exceeded",
            "allow_auto_action": random.choice([True,False]),
            "manual_review_required": random.choice([True,False]),
            "platform_action_status": random.choice(["pending","done","failed"]),
            "platform_action_response": "{}",
            "evidence_report_path": f"report_{i}.json",
            "created_at": datetime.utcnow()-timedelta(hours=i*3),
            "updated_at": datetime.utcnow()-timedelta(hours=i),
        })
    return cases

def _demo_stats() -> dict:
    return {"total":120,"pending":18,"approved":74,"rejected":22,"error":6,
            "high_risk":31,"medium_risk":55,"low_risk":34,"needs_review":18}

def _demo_logs(n: int = 40) -> list[dict]:
    random.seed(7)
    actions = ["auto_approved","manual_approved","manual_rejected",
               "retry_requested","case_created"]
    logs = []
    for i in range(n):
        logs.append({
            "id": i+1, "case_id": f"CASE-{1000+(i%30)}",
            "platform": random.choice(_PLATFORMS),
            "action_type": random.choice(actions),
            "status": random.choice(["success","failed"]),
            "details": json.dumps({"note": f"demo log {i}"}),
            "created_at": datetime.utcnow()-timedelta(minutes=i*17),
        })
    return logs

def _safe_int(v) -> int:
    try:
        f = float(v)
        return 0 if (f != f or f in (float("inf"), float("-inf"))) else int(f)
    except Exception:
        return 0

def _safe_get_stats() -> dict:
    try:
        return {k: _safe_int(v) for k, v in get_case_stats().items()}
    except Exception:
        return _demo_stats()

def _safe_get_cases(**kw) -> list[dict]:
    try:
        return get_cases(**kw)
    except Exception:
        cases = _demo_cases()
        if kw.get("status"):
            cases = [c for c in cases if c["status"] == kw["status"]]
        if kw.get("risk_level"):
            cases = [c for c in cases if c["risk_level"] == kw["risk_level"]]
        return cases[:kw.get("limit",100)]

def _safe_get_logs(**kw) -> list[dict]:
    try:
        return get_audit_logs(**kw)
    except Exception:
        logs = _demo_logs()
        if kw.get("case_id"):
            logs = [lo for lo in logs if lo["case_id"] == kw["case_id"]]
        return logs

_RISK_EMOJI  = {"high":"🔴","medium":"🟡","low":"🟢"}
_RISK_COLOUR = {"high":"#dc2626","medium":"#d97706","low":"#059669"}
_RISK_BG     = {"high":"#fee2e2","medium":"#fef3c7","low":"#d1fae5"}

def _html_bars(items: list[tuple[str,int,str]], title: str):
    mx = max((v for _,v,_ in items), default=1) or 1
    bars = ""
    for label, value, colour in items:
        pct = int(value/mx*100)
        bars += f"""
        <div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:.78rem;font-weight:600;color:#374151;">{label}</span>
                <span style="font-size:.78rem;font-weight:800;color:{colour};">{value}</span>
            </div>
            <div style="background:#f0f4ff;border-radius:8px;height:10px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;
                            background:linear-gradient(90deg,{colour},{colour}99);
                            border-radius:8px;transition:width .6s ease;"></div>
            </div>
        </div>"""
    st.markdown(f"""
        <div style="background:#fff;border:2px solid #e8ecff;border-radius:16px;
                    padding:20px;box-shadow:0 4px 16px rgba(99,102,241,.07);">
            <div style="font-weight:700;color:#1a1d2e;margin-bottom:16px;">{title}</div>
            {bars}
        </div>""", unsafe_allow_html=True)


# ── 1. Overview ───────────────────────────────────────────────────────────────
def render_overview():
    require("view")
    s = _safe_get_stats()
    st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px;">
            <div style="background:#fff;border-radius:14px;padding:18px;border:2px solid #e8ecff;
                        text-align:center;box-shadow:0 4px 14px rgba(99,102,241,.08);">
                <div style="font-size:.68rem;color:#6b7280;font-weight:700;
                            text-transform:uppercase;">Total</div>
                <div style="font-size:2rem;font-weight:800;color:#1a1d2e;margin-top:4px;">
                    {s.get("total",0)}</div></div>
            <div style="background:#fffbeb;border-radius:14px;padding:18px;border:2px solid #fde68a;
                        text-align:center;">
                <div style="font-size:.68rem;color:#92400e;font-weight:700;
                            text-transform:uppercase;">⏳ Pending</div>
                <div style="font-size:2rem;font-weight:800;color:#d97706;margin-top:4px;">
                    {s.get("pending",0)}</div></div>
            <div style="background:#ecfdf5;border-radius:14px;padding:18px;border:2px solid #6ee7b7;
                        text-align:center;">
                <div style="font-size:.68rem;color:#065f46;font-weight:700;
                            text-transform:uppercase;">✅ Approved</div>
                <div style="font-size:2rem;font-weight:800;color:#059669;margin-top:4px;">
                    {s.get("approved",0)}</div></div>
            <div style="background:#fef2f2;border-radius:14px;padding:18px;border:2px solid #fca5a5;
                        text-align:center;">
                <div style="font-size:.68rem;color:#991b1b;font-weight:700;
                            text-transform:uppercase;">❌ Rejected</div>
                <div style="font-size:2rem;font-weight:800;color:#dc2626;margin-top:4px;">
                    {s.get("rejected",0)}</div></div>
            <div style="background:#eff6ff;border-radius:14px;padding:18px;border:2px solid #93c5fd;
                        text-align:center;">
                <div style="font-size:.68rem;color:#1e40af;font-weight:700;
                            text-transform:uppercase;">⚠️ Review</div>
                <div style="font-size:2rem;font-weight:800;color:#3b82f6;margin-top:4px;">
                    {s.get("needs_review",0)}</div></div>
        </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        _html_bars([("🔴 High",  s.get("high_risk",0),   "#dc2626"),
                    ("🟡 Medium",s.get("medium_risk",0),  "#d97706"),
                    ("🟢 Low",   s.get("low_risk",0),     "#059669")],
                   "📊 Risk Level Breakdown")
    with c2:
        _html_bars([("⏳ Pending",  s.get("pending",0),   "#d97706"),
                    ("✅ Approved", s.get("approved",0),  "#059669"),
                    ("❌ Rejected", s.get("rejected",0),  "#dc2626"),
                    ("💥 Error",    s.get("error",0),     "#6366f1")],
                   "📈 Status Distribution")

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin:24px 0 10px;'>"
                "🕐 Recent Audit Activity</div>", unsafe_allow_html=True)
    logs = _safe_get_logs(limit=10)
    if logs:
        df = pd.DataFrame(logs)
        cols = [c for c in ["created_at","case_id","platform","action_type","status"]
                if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity.")


# ── 2. Alerts ─────────────────────────────────────────────────────────────────
def render_alerts():
    require("view")
    st.markdown("""
        <style>
        .a-card{background:#fff;border:2px solid #e8ecff;border-radius:16px;
                margin-bottom:14px;overflow:hidden;
                box-shadow:0 2px 12px rgba(99,102,241,.07);}
        .a-card:hover{box-shadow:0 6px 24px rgba(99,102,241,.15);}
        .a-hdr{display:flex;align-items:center;gap:14px;padding:14px 20px;}
        .a-badge{display:inline-block;padding:3px 11px;border-radius:20px;
                 font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;}
        .sc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:0 18px 16px;}
        .sc-box{background:#f8f9ff;border:1px solid #e8ecff;border-radius:10px;
                padding:10px;text-align:center;}
        .sc-lbl{font-size:.62rem;color:#9ca3af;font-weight:700;text-transform:uppercase;}
        .sc-val{font-size:1rem;font-weight:800;color:#1a1d2e;margin-top:2px;}
        .a-div{height:1px;background:#e8ecff;margin:0 18px 14px;}
        </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        risk_filter = st.selectbox("Filter by risk",["All","high","medium","low"],key="a_risk")
    with c2:
        limit = st.slider("Max cases",5,100,25,key="a_limit")

    kw: dict = {"status":"pending","limit":limit}
    if risk_filter != "All":
        kw["risk_level"] = risk_filter
    cases = _safe_get_cases(**kw)

    if not cases:
        st.success("✅ No cases pending manual review.")
        return

    st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fff7ed,#fef3c7);
                    border:2px solid #fde68a;border-radius:12px;
                    padding:12px 18px;margin:12px 0 18px;
                    display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.3rem;">🚨</span>
            <div>
                <span style="font-weight:700;color:#92400e;">
                    {len(cases)} case(s) awaiting review</span>
                <div style="font-size:.72rem;color:#b45309;margin-top:1px;">
                    Review each case and take action</div>
            </div>
        </div>""", unsafe_allow_html=True)

    reviewer = st.session_state.get("username","unknown")

    for case in cases:
        cid       = case["case_id"]
        risk      = case.get("risk_level","unknown")
        platform  = case.get("platform","—")
        conf      = case.get("match_confidence",0) or 0
        deepfake  = case.get("deepfake_score",0) or 0
        nudity    = case.get("nudity_score",0) or 0
        post_url  = case.get("post_url","")
        r_e = _RISK_EMOJI.get(risk,"⚪")
        r_c = _RISK_COLOUR.get(risk,"#6b7280")
        r_b = _RISK_BG.get(risk,"#f9fafb")
        url_html = (f"<div style='padding:0 18px 12px;font-size:.76rem;color:#6b7280;'>"
                    f"🔗 <a href='{post_url}' target='_blank' "
                    f"style='color:#6366f1;font-weight:500;text-decoration:none;'>"
                    f"{post_url}</a></div>") if post_url else ""

        st.markdown(f"""
            <div class="a-card">
                <div class="a-hdr" style="background:linear-gradient(135deg,{r_b},{r_b}88);">
                    <div style="font-size:1.5rem;flex-shrink:0;">{r_e}</div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:800;font-size:.95rem;color:#1a1d2e;
                                    white-space:nowrap;overflow:hidden;
                                    text-overflow:ellipsis;">{cid}</div>
                        <div style="display:flex;gap:6px;margin-top:4px;flex-wrap:wrap;">
                            <span class="a-badge"
                                  style="background:{r_b};color:{r_c};
                                         border:1.5px solid {r_c};">{risk.upper()} RISK</span>
                            <span class="a-badge"
                                  style="background:#f0f4ff;color:#6366f1;
                                         border:1.5px solid #c7d2fe;">{platform}</span>
                        </div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <div style="font-size:1.2rem;font-weight:800;color:{r_c};">
                            {conf:.1%}</div>
                        <div style="font-size:.62rem;color:#9ca3af;font-weight:600;">
                            CONFIDENCE</div>
                    </div>
                </div>
                <div class="sc-grid">
                    <div class="sc-box"><div class="sc-lbl">Match</div>
                        <div class="sc-val">{conf:.3f}</div></div>
                    <div class="sc-box"><div class="sc-lbl">Deepfake</div>
                        <div class="sc-val">{deepfake:.3f}</div></div>
                    <div class="sc-box"><div class="sc-lbl">Nudity</div>
                        <div class="sc-val">{nudity:.3f}</div></div>
                    <div class="sc-box"><div class="sc-lbl">Platform</div>
                        <div class="sc-val" style="font-size:.8rem;">{platform}</div></div>
                </div>
                {url_html}
                <div class="a-div"></div>
            </div>""", unsafe_allow_html=True)

        if can("approve") or can("reject") or can("retry"):
            b1, b2, b3, _ = st.columns([1,1,1,3])
            with b1:
                if can("approve") and st.button("✅ Approve",key=f"app_{cid}",
                                                use_container_width=True):
                    res = approve_case(cid, reviewer)
                    st.success(f"Approved {cid}") if res["success"] \
                        else st.error(res["error"])
            with b2:
                if can("reject") and st.button("❌ Reject",key=f"rej_{cid}",
                                               use_container_width=True):
                    res = reject_case(cid, reviewer, reason="Manual rejection")
                    st.warning(f"Rejected {cid}") if res["success"] \
                        else st.error(res["error"])
            with b3:
                if can("retry") and st.button("🔁 Retry",key=f"ret_{cid}",
                                              use_container_width=True):
                    res = retry_case(cid, reviewer)
                    st.info(f"Retry queued: {cid}") if res["success"] \
                        else st.error(res["error"])
        else:
            st.warning("⛔ No permission to act on cases.")
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)


# ── 3. Case Details ────────────────────────────────────────────────────────────
def render_case_details():
    require("view")
    case_id = st.text_input("Enter Case ID", placeholder="CASE-1000")
    if not case_id:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#f0f4ff,#e8ecff);
                        border:2px solid #c7d2fe;border-radius:16px;
                        padding:40px;text-align:center;margin-top:16px;">
                <div style="font-size:2.5rem;margin-bottom:12px;">🔍</div>
                <div style="font-weight:700;color:#1a1d2e;">Enter a Case ID above</div>
                <div style="color:#6b7280;font-size:.85rem;margin-top:6px;">
                    e.g. CASE-1000, CASE-1001 …</div>
            </div>""", unsafe_allow_html=True)
        return

    try:
        case = get_case_by_id(case_id)
    except Exception:
        case = {c["case_id"]: c for c in _demo_cases()}.get(case_id)

    if not case:
        st.error(f"Case `{case_id}` not found.")
        return

    risk = case.get("risk_level","unknown")
    r_e  = _RISK_EMOJI.get(risk,"⚪")
    r_c  = _RISK_COLOUR.get(risk,"#6b7280")
    r_b  = _RISK_BG.get(risk,"#f9fafb")

    st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f0f4ff,#e8ecff);
                    border:2px solid #c7d2fe;border-radius:18px;
                    padding:22px 26px;margin-bottom:22px;
                    display:flex;align-items:center;gap:18px;">
            <div style="font-size:2.2rem;">{r_e}</div>
            <div style="flex:1;">
                <div style="font-size:1.3rem;font-weight:800;color:#1a1d2e;">
                    {case.get("case_id")}</div>
                <div style="display:flex;gap:8px;margin-top:6px;flex-wrap:wrap;">
                    <span style="background:{r_b};color:{r_c};border:1.5px solid {r_c};
                                 border-radius:20px;padding:3px 12px;font-size:.7rem;
                                 font-weight:700;text-transform:uppercase;">
                        {risk.upper()} RISK</span>
                    <span style="background:#f0f4ff;color:#6366f1;border:1.5px solid #c7d2fe;
                                 border-radius:20px;padding:3px 12px;font-size:.7rem;
                                 font-weight:600;">
                        {case.get("platform","—").upper()}</span>
                    <span style="background:#f0fdf4;color:#059669;border:1.5px solid #6ee7b7;
                                 border-radius:20px;padding:3px 12px;font-size:.7rem;
                                 font-weight:600;">
                        {case.get("status","—").upper()}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin-bottom:10px;'>"
                "📐 Detection Scores</div>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    s1.metric("Match Confidence", f"{case.get('match_confidence') or 0:.3f}")
    s2.metric("Match Distance",   f"{case.get('match_distance') or 0:.3f}")
    s3.metric("Deepfake Score",   f"{case.get('deepfake_score') or 0:.3f}")
    s4.metric("Nudity Score",     f"{case.get('nudity_score') or 0:.3f}")

    for sec, data in [
        ("📋 Compliance Decision", {
            "compliance_reason":      case.get("compliance_reason"),
            "allow_auto_action":      case.get("allow_auto_action"),
            "manual_review_required": case.get("manual_review_required"),
        }),
        ("🌐 Platform Action", {
            "platform_action_status":   case.get("platform_action_status"),
            "platform_action_response": case.get("platform_action_response"),
            "post_url":                 case.get("post_url"),
        }),
    ]:
        st.markdown(f"<div style='font-weight:700;color:#1a1d2e;margin:18px 0 8px;'>"
                    f"{sec}</div>", unsafe_allow_html=True)
        st.json(data)

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin:18px 0 8px;'>"
                "⚖️ Thresholds Snapshot</div>", unsafe_allow_html=True)
    t = case.get("thresholds_snapshot")
    if t:
        try:
            st.json(json.loads(t) if isinstance(t, str) else t)
        except Exception:
            st.code(str(t))
    else:
        st.info("No threshold snapshot available.")

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin:18px 0 8px;'>"
                "📦 Evidence Packet</div>", unsafe_allow_html=True)
    rp = case.get("evidence_report_path")
    if rp:
        try:
            ev = load_evidence_report(rp)
            if ev:
                st.json(ev)
                st.download_button("⬇️ Download Evidence JSON",
                    data=json.dumps(ev,indent=2,default=str),
                    file_name=f"evidence_{case_id}.json", mime="application/json")
            else:
                st.warning("Evidence file not found on disk.")
        except Exception as e:
            st.error(f"Could not load evidence: {e}")
    else:
        st.info("No evidence report path recorded.")

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin:18px 0 8px;'>"
                "🕐 Audit Timeline</div>", unsafe_allow_html=True)
    logs = _safe_get_logs(case_id=case_id, limit=50)
    if logs:
        df = pd.DataFrame(logs)
        cols = [c for c in ["created_at","action_type","status","details"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No audit entries for this case.")


# ── 4. Reports ────────────────────────────────────────────────────────────────
def render_reports():
    require("view")
    c1,c2,c3 = st.columns(3)
    with c1: sf  = st.selectbox("Status",["All","pending","approved","rejected","error"])
    with c2: rf  = st.selectbox("Risk Level",["All","high","medium","low"])
    with c3: lim = st.slider("Max results",10,200,50)

    kw: dict = {"limit":lim}
    if sf != "All":  kw["status"]     = sf
    if rf != "All":  kw["risk_level"] = rf
    cases = _safe_get_cases(**kw)

    if not cases:
        st.info("No cases match the selected filters.")
        return

    df = pd.DataFrame(cases)
    cols = [c for c in ["case_id","platform","status","risk_level",
                         "match_confidence","deepfake_score","nudity_score",
                         "evidence_report_path","created_at"] if c in df.columns]
    st.markdown(f"<div style='font-weight:600;color:#6366f1;margin-bottom:10px;'>"
                f"📄 {len(cases)} report(s) found</div>", unsafe_allow_html=True)
    st.dataframe(df[cols], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download as CSV",
                       data=df[cols].to_csv(index=False),
                       file_name="reports_export.csv", mime="text/csv")


# ── 5. Audit Logs ─────────────────────────────────────────────────────────────
def render_audit_logs():
    require("view")
    c1,c2,c3 = st.columns(3)
    with c1: cid_f = st.text_input("Filter by Case ID", placeholder="CASE-1000")
    with c2: act_f = st.selectbox("Action Type",
                ["All","auto_approved","manual_approved","manual_rejected",
                 "retry_requested","case_created"])
    with c3: lim = st.slider("Max entries",10,500,100)

    kw: dict = {"limit":lim}
    if cid_f.strip():       kw["case_id"]     = cid_f.strip()
    if act_f != "All":      kw["action_type"] = act_f
    logs = _safe_get_logs(**kw)

    if not logs:
        st.info("No audit log entries match the selected filters.")
        return

    df = pd.DataFrame(logs)
    cols = [c for c in ["id","created_at","case_id","platform",
                         "action_type","status","details"] if c in df.columns]
    st.markdown(f"<div style='font-weight:600;color:#6366f1;margin-bottom:10px;'>"
                f"📋 {len(logs)} log entry/entries</div>", unsafe_allow_html=True)
    st.dataframe(df[cols], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download Logs as CSV",
                       data=df[cols].to_csv(index=False),
                       file_name="audit_logs_export.csv", mime="text/csv")


# ── 6. Admin ──────────────────────────────────────────────────────────────────
def render_admin():
    require("manage_accounts")

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin-bottom:10px;'>"
                "🔌 Member 4 API Health</div>", unsafe_allow_html=True)
    if st.button("Run Health Check"):
        r = health_check()
        st.success(f"✅ Healthy — {r['data']}") if r["success"] \
            else st.error(f"❌ Unreachable — {r['error']}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin-bottom:10px;'>"
                "👥 Team Accounts</div>", unsafe_allow_html=True)
    from authentication import ACCOUNTS
    st.dataframe(pd.DataFrame([{"username":u,"role":i["role"]}
                                for u,i in ACCOUNTS.items()]),
                 use_container_width=True, hide_index=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if can("force_action"):
        st.markdown("<div style='font-weight:700;color:#1a1d2e;margin-bottom:10px;'>"
                    "⚡ Force Action</div>", unsafe_allow_html=True)
        f1,f2 = st.columns(2)
        with f1:
            fid  = st.text_input("Case ID",key="force_cid",placeholder="CASE-1000")
            fact = st.selectbox("Action",["approve","reject","retry"],key="force_act")
        with f2:
            fnotes = st.text_area("Notes / reason",key="force_notes",height=120)
        if st.button("⚡ Execute"):
            reviewer = st.session_state.get("username","admin")
            if fact == "approve":   res = approve_case(fid, reviewer, notes=fnotes)
            elif fact == "reject":  res = reject_case(fid, reviewer, reason=fnotes)
            else:                   res = retry_case(fid, reviewer)
            st.success(f"✅ Force-{fact} sent for `{fid}`") if res["success"] \
                else st.error(f"❌ {res['error']}")
        st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div style='font-weight:700;color:#1a1d2e;margin-bottom:10px;'>"
                "🔧 System Config</div>", unsafe_allow_html=True)
    import os
    st.json({
        "DATABASE_URL":     os.environ.get("DATABASE_URL","(not set)"),
        "MEMBER4_BASE_URL": os.environ.get("MEMBER4_BASE_URL","http://localhost:8004"),
        "REPORTS_DIR":      os.environ.get("REPORTS_DIR","reports"),
    })