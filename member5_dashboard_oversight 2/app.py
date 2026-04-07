import streamlit as st

st.set_page_config(
    page_title="Deepfake Threat Oversight Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hide sidebar collapse button — CORRECT selector for Streamlit 1.32+ ───────
st.markdown("""
    <style>
    /* THE correct selector — hides the collapse/expand arrow button */
    [data-testid="baseButton-headerSidebarCollapse"] {
        display: none !important;
    }
    /* fallback selectors for older versions */
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="collapsedControl"]           { display: none !important; }
    button[kind="header"]                      { display: none !important; }
    /* nuclear option — hide any button inside the sidebar header area */
    [data-testid="stSidebar"] > div:first-child > div > button {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

from authentication import is_authenticated, render_login_page, ACCOUNTS
from dashboard_routes import (
    render_overview, render_alerts, render_case_details,
    render_reports, render_audit_logs, render_admin,
)

# ── Login gate ────────────────────────────────────────────────────────────────
if not is_authenticated():
    render_login_page()
    st.stop()

# ── Session values ────────────────────────────────────────────────────────────
role     = st.session_state.get("role", "reviewer")
username = st.session_state.get("username", "")
r_icon   = "👑" if role == "admin" else "👤"

pages = ["Overview", "Alerts", "Case Details", "Reports", "Audit Logs"]
if role == "admin":
    pages.append("Admin")

_ICONS = {
    "Overview":     "📊",
    "Alerts":       "🚨",
    "Case Details": "🔍",
    "Reports":      "📂",
    "Audit Logs":   "📋",
    "Admin":        "⚙️",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <style>
        @keyframes sbpulse {{
            0%,100% {{ box-shadow: 0 8px 24px rgba(99,102,241,.4); }}
            50%      {{ box-shadow: 0 12px 32px rgba(99,102,241,.7);
                        transform: translateY(-2px); }}
        }}
        .sb-brand {{
            background: linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#ec4899 100%);
            border-radius: 16px; padding: 18px; text-align: center;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(99,102,241,.35);
            animation: sbpulse 3s ease-in-out infinite;
        }}
        .sb-brand-icon  {{ font-size:2.2rem; line-height:1; }}
        .sb-brand-title {{ color:#fff!important; font-weight:800;
                           font-size:1.1rem; margin-top:6px; }}
        .sb-brand-sub   {{ color:rgba(255,255,255,.8)!important; font-size:.65rem;
                           text-transform:uppercase; letter-spacing:.1em;
                           margin-top:3px; }}
        .sb-user {{
            background: linear-gradient(135deg,#f0f4ff,#e8ecff);
            border: 2px solid #e0e7ff; border-radius: 12px;
            padding: 10px 14px; margin-bottom: 12px;
            display: flex; align-items: center; gap: 10px;
        }}
        .sb-user-name {{ font-weight:700; color:#1a1d2e!important; font-size:.9rem; }}
        .sb-user-role {{ font-size:.7rem; color:#6366f1!important; font-weight:600;
                         text-transform:uppercase; letter-spacing:.08em; }}
        .sb-nav-lbl   {{ font-size:.7rem; color:#9ca3af!important;
                         text-transform:uppercase; letter-spacing:.1em;
                         font-weight:600; margin:8px 0 6px; padding-left:4px; }}
        .sb-ver {{
            margin-top:16px; padding:10px;
            background:linear-gradient(135deg,#f0f4ff,#e8ecff);
            border-radius:10px; border:1px solid #e0e7ff; text-align:center;
        }}
        .sb-ver-lbl {{ font-size:.62rem; color:#9ca3af!important; font-weight:600;
                       text-transform:uppercase; letter-spacing:.08em; }}
        .sb-ver-val {{ font-size:.8rem; color:#6366f1!important;
                       font-weight:700; margin-top:2px; }}

        /* radio nav pills */
        [data-testid="stSidebar"] .stRadio > div {{ gap:4px!important; }}
        [data-testid="stSidebar"] .stRadio > div > label {{
            background:#f8f9ff!important;
            border:1.5px solid #e2e8f0!important;
            border-radius:10px!important;
            padding:10px 14px!important;
            margin:2px 0!important;
            font-weight:500!important;
            color:#374151!important;
            cursor:pointer!important;
            transition:all .25s ease!important;
            display:block!important;
        }}
        [data-testid="stSidebar"] .stRadio > div > label:hover {{
            background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;
            color:#fff!important;
            border-color:transparent!important;
            transform:translateX(4px)!important;
            box-shadow:0 4px 15px rgba(99,102,241,.35)!important;
        }}
        /* logout button red */
        [data-testid="stSidebar"] .stButton > button {{
            background:linear-gradient(135deg,#ef4444,#dc2626)!important;
            color:#fff!important; border:none!important;
            border-radius:10px!important; font-weight:600!important;
            width:100%!important; padding:10px!important;
            transition:all .3s ease!important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            transform:translateY(-2px)!important;
            box-shadow:0 8px 20px rgba(239,68,68,.45)!important;
        }}
        [data-testid="stSidebarNav"] {{ display:none!important; }}
        </style>

    <div class="sb-brand">
        <div class="sb-brand-icon">🕵️‍♂️</div>
        <div class="sb-brand-title">Identity Command</div>
        <div class="sb-brand-sub">Deepfake Detection & Oversight</div>
    </div>

    <div class="sb-user">
        <span style="font-size:1.4rem;">{r_icon}</span>
        <div>
            <div class="sb-user-name">{username}</div>
            <div class="sb-user-role">SYSTEM {role.upper()}</div>
        </div>
    </div>

        <div class="sb-nav-lbl">Navigation</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        pages,
        format_func=lambda p: f"{_ICONS.get(p, '')}  {p}",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if st.button("🚪  Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("""
        <div class="sb-ver">
            <div class="sb-ver-lbl">Version</div>
            <div class="sb-ver-val">v1.0.0 · 2026</div>
        </div>
    """, unsafe_allow_html=True)

# ── Main app CSS ──────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main .block-container {
        background: #f0f4ff !important;
        font-family: 'Inter', sans-serif !important;
        color: #1a1d2e !important;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg,
            #f0f4ff 0%, #e8f0fe 25%, #f3e8ff 50%,
            #fce8f3 75%, #e8f8f0 100%) !important;
        background-size: 400% 400% !important;
        animation: gradShift 12s ease infinite !important;
    }
    @keyframes gradShift {
        0%  { background-position: 0%   50%; }
        50% { background-position: 100% 50%; }
        100%{ background-position: 0%   50%; }
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#ffffff 0%,#f8f9ff 100%) !important;
        border-right: 2px solid #e2e8f0 !important;
        box-shadow: 4px 0 24px rgba(99,102,241,.08) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div { color: #1a1d2e !important; }

    .main .stButton > button {
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
        padding: 10px 20px !important; transition: all .3s ease !important;
        box-shadow: 0 4px 15px rgba(99,102,241,.3) !important;
    }
    .main .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99,102,241,.45) !important;
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: #fff !important; color: #1a1d2e !important;
        border: 2px solid #e2e8f0 !important; border-radius: 10px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,.15) !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #fff !important; color: #1a1d2e !important;
        border: 2px solid #e2e8f0 !important; border-radius: 10px !important;
    }

    [data-testid="stMetric"] {
        background: #fff !important; border-radius: 16px !important;
        padding: 20px !important; border: 2px solid #e8ecff !important;
        box-shadow: 0 4px 20px rgba(99,102,241,.08) !important;
        transition: transform .25s, box-shadow .25s !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 32px rgba(99,102,241,.18) !important;
    }
    [data-testid="stMetricLabel"] {
        color: #6b7280 !important; font-weight: 600 !important;
        font-size: .75rem !important; text-transform: uppercase !important;
    }
    [data-testid="stMetricValue"] {
        color: #1a1d2e !important; font-weight: 800 !important;
        font-size: 2rem !important;
    }

    [data-testid="stDataFrame"] {
        background: #fff !important; border-radius: 14px !important;
        border: 2px solid #e8ecff !important;
        box-shadow: 0 4px 20px rgba(99,102,241,.08) !important;
    }

    .stSuccess>div { background:#ecfdf5!important; border:2px solid #10b981!important;
                     border-radius:12px!important; color:#065f46!important; }
    .stError>div   { background:#fef2f2!important; border:2px solid #ef4444!important;
                     border-radius:12px!important; color:#991b1b!important; }
    .stWarning>div { background:#fffbeb!important; border:2px solid #f59e0b!important;
                     border-radius:12px!important; color:#92400e!important; }
    .stInfo>div    { background:#eff6ff!important; border:2px solid #3b82f6!important;
                     border-radius:12px!important; color:#1e40af!important; }

    h1,h2,h3,h4,h5,h6 { color:#1a1d2e!important; font-family:'Inter',sans-serif!important; }
    p,span,label,div   { color:#374151!important; font-family:'Inter',sans-serif!important; }
    code {
        background:#f0f4ff!important; color:#6366f1!important;
        border-radius:6px!important; padding:2px 8px!important;
        font-family:'JetBrains Mono',monospace!important;
        border:1px solid #e0e7ff!important;
    }
    hr {
        border:none!important; height:2px!important;
        background:linear-gradient(90deg,#6366f1,#8b5cf6,#ec4899,transparent)!important;
        margin:16px 0!important;
    }
    ::-webkit-scrollbar { width:6px; height:6px; }
    ::-webkit-scrollbar-track { background:#f0f4ff; border-radius:3px; }
    ::-webkit-scrollbar-thumb {
        background:linear-gradient(180deg,#6366f1,#8b5cf6); border-radius:3px;
    }
    .stDownloadButton > button {
        background:linear-gradient(135deg,#10b981,#059669)!important;
        color:#fff!important; border:none!important;
        border-radius:10px!important; font-weight:600!important;
        box-shadow:0 4px 15px rgba(16,185,129,.3)!important;
    }

    @keyframes fadeIn      { from{opacity:0} to{opacity:1} }
    @keyframes fadeSlideUp { from{opacity:0;transform:translateY(16px)}
                              to{opacity:1;transform:translateY(0)} }
    @keyframes float1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-20px,25px)} }
    @keyframes float2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-20px)} }

    .main .block-container {
        animation: fadeIn .5s ease !important;
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }
    .page-hdr {
        background: linear-gradient(135deg,#ffffff,#f8f9ff);
        border: 2px solid #e8ecff; border-radius: 18px;
        padding: 22px 28px; margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(99,102,241,.08);
        animation: fadeSlideUp .4s ease;
    }
    #MainMenu { visibility:hidden; }
    footer     { visibility:hidden; }
    header     { visibility:hidden; }
    </style>

    <div style="position:fixed;top:0;left:0;width:100%;height:100%;
                pointer-events:none;z-index:0;overflow:hidden;">
        <div style="position:absolute;width:300px;height:300px;
                    background:radial-gradient(circle,rgba(99,102,241,.07) 0%,transparent 70%);
                    top:-100px;right:-80px;
                    animation:float1 8s ease-in-out infinite;"></div>
        <div style="position:absolute;width:200px;height:200px;
                    background:radial-gradient(circle,rgba(139,92,246,.07) 0%,transparent 70%);
                    bottom:80px;left:-40px;
                    animation:float2 10s ease-in-out infinite;"></div>
    </div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
_META = {
    "Overview":     ("📊", "Threat Overview", "Live detection stats, risk grading, and mitigation activity"),
    "Alerts":       ("🚨", "Detection Queue", "High-confidence threats awaiting automated or manual mitigation"),
    "Case Details": ("🔍", "Forensic Analysis", "Detailed deepfake artifact metadata and matching evidence"),
    "Reports":      ("📂", "Evidence Library", "Standardized forensic reports and compliance exports"),
    "Audit Logs":   ("📋", "Chain of Custody", "Immutable record of system detections and mitigation steps"),
    "Admin":        ("⚙️", "System Config", "Onboarding keys, health checks and AI model parameters"),
}
icon, title, desc = _META.get(page, ("🛡️", page, ""))

st.markdown(f"""
    <div class="page-hdr">
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                        border-radius:14px;padding:14px;flex-shrink:0;
                        box-shadow:0 4px 16px rgba(99,102,241,.35);
                        font-size:1.6rem;line-height:1;">{icon}</div>
            <div>
                <h2 style="margin:0;font-size:1.5rem;font-weight:800;
                           background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
                           -webkit-background-clip:text;
                           -webkit-text-fill-color:transparent;
                           background-clip:text;">{title}</h2>
                <p style="margin:4px 0 0;color:#6b7280;font-size:.85rem;">{desc}</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── Route ─────────────────────────────────────────────────────────────────────
if   page == "Overview":      render_overview()
elif page == "Alerts":        render_alerts()
elif page == "Case Details":  render_case_details()
elif page == "Reports":       render_reports()
elif page == "Audit Logs":    render_audit_logs()
elif page == "Admin":         render_admin()