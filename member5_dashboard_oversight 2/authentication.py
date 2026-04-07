import os
import hashlib
import hmac
import streamlit as st


def _hash_password(password: str, salt: bytes = None, iterations: int = 260000) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"{iterations}:{salt.hex()}:{dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        iters, salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        dk   = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


_DEFAULTS = {
    "admin":     ("admin",     "1234",         "admin"),
    "reviewer1": ("reviewer1", "Review@001!",  "reviewer"),
    "reviewer2": ("reviewer2", "Review@002!",  "reviewer"),
    "reviewer3": ("reviewer3", "Review@003!",  "reviewer"),
    "reviewer4": ("reviewer4", "Review@004!",  "reviewer"),
}


def _build_accounts() -> dict:
    env_map = {
        "admin":     ("ADMIN_USER",     "ADMIN_HASH"),
        "reviewer1": ("REVIEWER1_USER", "REVIEWER1_HASH"),
        "reviewer2": ("REVIEWER2_USER", "REVIEWER2_HASH"),
        "reviewer3": ("REVIEWER3_USER", "REVIEWER3_HASH"),
        "reviewer4": ("REVIEWER4_USER", "REVIEWER4_HASH"),
    }
    accounts = {}
    for key, (uenv, henv) in env_map.items():
        _, default_pass, role = _DEFAULTS[key]
        username = os.environ.get(uenv, key)
        stored   = os.environ.get(henv, _hash_password(default_pass))
        accounts[username] = {"hash": stored, "role": role}
    return accounts


ACCOUNTS: dict = _build_accounts()


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def logout():
    st.session_state.clear()


# ── NO CSS HERE AT ALL ────────────────────────────────────────────────────────
def render_login_page():
    st.title("🕵️‍♂️ Identity Command")
    st.markdown("#### Deepfake Detection & Oversight Command Center")
    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("### Sign In")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", placeholder="Enter password",
                                 type="password")
        if st.button("Login →", use_container_width=True):
            acct = ACCOUNTS.get(username)
            if acct and verify_password(password, acct["hash"]):
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username
                st.session_state["role"]          = acct["role"]
                st.rerun()
            else:
                st.error("⚠️ Invalid username or password.")
        st.divider()
        st.info("**Default:** admin / 1234\n\nreviewer1–4 / Review@001–004!")