import sys, os, types
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = types.ModuleType("streamlit")

_st = sys.modules["streamlit"]
_st.session_state = {}
_st.error = lambda *a,**k: None
_st.stop  = lambda: None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from authentication import _hash_password, verify_password, ACCOUNTS, is_authenticated, logout

class TestVerify:
    def test_correct(self):          assert verify_password("MySecret1!", _hash_password("MySecret1!"))
    def test_wrong(self):            assert not verify_password("Wrong", _hash_password("Right"))
    def test_empty(self):            assert not verify_password("", _hash_password("Something"))
    def test_five_accounts(self):    assert len(ACCOUNTS) == 5
    def test_one_admin(self):        assert sum(1 for i in ACCOUNTS.values() if i["role"]=="admin") == 1
    def test_four_reviewers(self):   assert sum(1 for i in ACCOUNTS.values() if i["role"]=="reviewer") == 4
    def test_unknown_user(self):     assert "hacker" not in ACCOUNTS
    def test_admin_creds(self):      assert verify_password("1234", ACCOUNTS["admin"]["hash"])
    def test_reviewer1_creds(self):  assert verify_password("Review@001!", ACCOUNTS["reviewer1"]["hash"])

class TestSession:
    def setup_method(self): _st.session_state.clear()
    def test_not_auth_empty(self):   assert not is_authenticated()
    def test_auth_after_set(self):
        _st.session_state["authenticated"] = True
        assert is_authenticated()
    def test_logout_clears(self):
        _st.session_state.update({"authenticated":True,"username":"admin","role":"admin"})
        logout()
        assert _st.session_state == {}
    def test_not_auth_after_logout(self):
        _st.session_state["authenticated"] = True
        logout()
        assert not is_authenticated()