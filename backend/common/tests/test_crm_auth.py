import pytest

from crm_auth import (
    TokenError,
    TokenExpiredError,
    TokenTypeError,
    role_allowed,
    verify_access_token,
    verify_refresh_token,
)

pytest.importorskip("jwt")
import jwt  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

SECRET = "test_secret_key_at_least_32_characters"


def _token(payload: dict) -> str:
    return jwt.encode(payload, SECRET, algorithm="HS256")


def _access(**overrides) -> str:
    payload = {
        "user_id": 1,
        "email": "user@example.test",
        "role": "admin",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    payload.update(overrides)
    return _token(payload)


def test_verify_access_token_ok():
    payload = verify_access_token(_access(), SECRET)
    assert payload["user_id"] == 1
    assert payload["role"] == "admin"


def test_access_token_missing_claim_rejected():
    token = _access()
    bad = jwt.decode(token, SECRET, algorithms=["HS256"])
    bad.pop("email")
    with pytest.raises(TokenError):
        verify_access_token(_token(bad), SECRET)


def test_refresh_token_rejected_as_access():
    refresh = _token(
        {
            "user_id": 1,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
    )
    with pytest.raises(TokenTypeError):
        verify_access_token(refresh, SECRET)


def test_expired_token_raises():
    expired = _access(exp=datetime.now(timezone.utc) - timedelta(minutes=1))
    with pytest.raises(TokenExpiredError):
        verify_access_token(expired, SECRET)


def test_verify_refresh_token_ok():
    refresh = _token(
        {
            "user_id": 7,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
    )
    payload = verify_refresh_token(refresh, SECRET)
    assert payload["user_id"] == 7


def test_role_allowed_case_insensitive():
    assert role_allowed("ADMIN", ("admin", "moderator"))
    assert not role_allowed("student", ("admin", "moderator"))
    assert not role_allowed(None, ("admin",))
