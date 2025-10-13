import pytest
from pydantic import ValidationError

from app.api.v1.auth import Register

VALID_EMAIL = "user@example.com"
VALID_NAME = "User Name"

def _make_register_req(password: str):
    return Register(email=VALID_EMAIL, name=VALID_NAME, password=password)

# TC-AUTH-PWD-01: Base scenario, password meets all policy rules
def test_password_base():
    pwd = "Abcdefghij!1" 
    user = _make_register_req(pwd)
    assert user.password == pwd

# TC-AUTH-PWD-02: Fails rules missing uppercase / special character
@pytest.mark.parametrize(
    "pwd, expect_fragment",
    [
        ("abcdefghijkl!", "uppercase"),
        ("ABCDEFGHIJKL1", "special"),
    ],
)
def test_password_fails_rule(pwd, expect_fragment):
    with pytest.raises(ValidationError) as ei:
        _make_register_req(pwd)
    assert expect_fragment in str(ei.value).lower()

# TC-AUTH-PWD-03:  Has whitespace
def test_password_has_whitespace():
    with pytest.raises(ValidationError) as ei:
        _make_register_req("Abcdef!ghi j")
    assert "whitespace" in str(ei.value).lower()

# TC-AUTH-PWD-04: Password is too short
def test_password_too_short():
    with pytest.raises(ValidationError) as ei:
        _make_register_req("Abcdef!ghi1") 
    errors = ei.value.errors()
    assert any(
        "too_short" in err.get("type", "") or "at least" in err.get("msg", "").lower()
        for err in errors
    )