import sys, os, types
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = types.ModuleType("streamlit")

_st = sys.modules["streamlit"]
_st.session_state = {}
_st.error = lambda *a,**k: None
_st.stop  = lambda: (_ for _ in ()).throw(SystemExit(0))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from data_access import FORBIDDEN_FIELDS, _strip_forbidden
from access_control import can

class TestDataSafety:
    def test_nonempty(self):        assert len(FORBIDDEN_FIELDS) > 0
    def test_embedding_stripped(self):
        assert "face_embedding" not in _strip_forbidden({"case_id":"X","face_embedding":b"\x00"})
    def test_all_stripped(self):
        row = {f:"S" for f in FORBIDDEN_FIELDS}; row["case_id"]="X"
        assert all(f not in _strip_forbidden(row) for f in FORBIDDEN_FIELDS)
    def test_allowed_pass(self):
        r = _strip_forbidden({"case_id":"X","platform":"tw","face_embedding":"bad"})
        assert r["case_id"]=="X" and r["platform"]=="tw" and "face_embedding" not in r

class TestAccessControl:
    def setup_method(self): _st.session_state.clear()
    def test_reviewer_view(self):
        _st.session_state["role"]="reviewer"; assert can("view")
    def test_reviewer_approve(self):
        _st.session_state["role"]="reviewer"; assert can("approve")
    def test_reviewer_no_manage(self):
        _st.session_state["role"]="reviewer"; assert not can("manage_accounts")
    def test_reviewer_no_force(self):
        _st.session_state["role"]="reviewer"; assert not can("force_action")
    def test_admin_manage(self):
        _st.session_state["role"]="admin"; assert can("manage_accounts")
    def test_unauth_no_view(self):
        assert not can("view")