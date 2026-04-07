import streamlit as st

PERMISSIONS: dict[str, set[str]] = {
    "admin": {
        "view", "approve", "reject", "retry",
        "manage_accounts", "force_action",
    },
    "reviewer": {
        "view", "approve", "reject", "retry",
    },
}


def get_role() -> str | None:
    return st.session_state.get("role")


def can(action: str) -> bool:
    role = get_role()
    if role is None:
        return False
    return action in PERMISSIONS.get(role, set())


def require(action: str):
    if not can(action):
        st.error(f"⛔ Access denied — requires permission: `{action}`")
        st.stop()