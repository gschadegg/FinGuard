import pytest
from types import SimpleNamespace

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError

from app.auth_settings import AuthSettings
from app.security.auth import get_current_user 
from app.domain.entities import UserEntity

from app.security import auth as _auth_module




class MockUserService():
    def __init__(self):
        self._user_by_id = {}  
        self._raised_exceptions = None 

        # number of get_user (by id)
        self.get_user_calls = []

    async def get_user(self, uid: int) -> UserEntity:
        self.get_user_calls.append({"uid": uid})

        if self._raised_exceptions:
            raise self._raised_exceptions
        return self._user_by_id.get(uid)


class MockAuthSettings(AuthSettings):
    def __init__(self):
        self.SECRET_KEY = "secretKey"
        self.ALGORITHM = "HS256"


@pytest.fixture
def token_credentials():
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="encoded.jwt.value")

@pytest.fixture
def settings():
    return MockAuthSettings()

@pytest.fixture
def user_svc():
    return MockUserService()



@pytest.fixture
def mock_jwt_decode(monkeypatch):
    calls = {"payload": None, "raise": None, "calls": []}

    def fake_decode(token, key, algorithms=None):
        calls["calls"].append({"token": token, "key": key, "algorithms": algorithms})
        if calls["raise"]:
            raise calls["raise"]
        return calls["payload"] or {}
    
    monkeypatch.setattr(_auth_module, "jwt", SimpleNamespace(decode=fake_decode))
    return calls


############################
# get_current_user Tests
############################



# TC-AUTH-GCU-001: Base scenario, gets a valid token and returns user
@pytest.mark.anyio
async def test_get_current_user_base(token_credentials, settings, user_svc, mock_jwt_decode):
    mock_jwt_decode["payload"] = {"uid": 42, "sub": "user@email.com"} 
    user_svc._user_by_id[42] = UserEntity(id=42, email="user@email.com", name="UserName")

    out_user = await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)

    # checks user is returned
    assert isinstance(out_user, UserEntity)
    assert (out_user.id, out_user.email) == (42, "user@email.com")

    # checks that djwt decode was called 
    decode_call = mock_jwt_decode["calls"][0]
    assert decode_call["token"] == "encoded.jwt.value"
    assert decode_call["key"] == settings.SECRET_KEY
    assert decode_call["algorithms"] == [settings.ALGORITHM]

    assert user_svc.get_user_calls == [{"uid": 42}]


# TC-AUTH-GCU-002: Missing user ID
@pytest.mark.anyio
async def test_get_current_user_missing_uid(token_credentials, settings, user_svc, mock_jwt_decode):
    mock_jwt_decode["payload"] = {"sub": "no-uid"}

    with pytest.raises(HTTPException) as ei:
        await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)
    exception = ei.value
    assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    # user_svc shouldnt be called since no id
    assert user_svc.get_user_calls == []


# TC-AUTH-GCU-003: Access token is expired
@pytest.mark.anyio
async def test_get_current_user_expired_token(token_credentials, settings, user_svc, mock_jwt_decode):

    mock_jwt_decode["raise"] = ExpiredSignatureError()
    with pytest.raises(HTTPException) as ei:
        await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)

    assert ei.value.status_code == status.HTTP_401_UNAUTHORIZED

    # user_svc shouldnt be called since bad token
    assert user_svc.get_user_calls == []  


# TC-AUTH-GCU-004: Access token is invalid
@pytest.mark.anyio
async def test_get_current_user_invalid_token(token_credentials, settings, user_svc, mock_jwt_decode):
    mock_jwt_decode["raise"] = InvalidTokenError("bad")

    with pytest.raises(HTTPException) as ei:
        await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)
    assert ei.value.status_code == status.HTTP_401_UNAUTHORIZED

    # user_svc shouldnt be called since bad token
    assert user_svc.get_user_calls == []


# TC-AUTH-GCU-005: User service throws exception when getting user
@pytest.mark.anyio
async def test_get_current_user_user_service_throws_error(token_credentials, settings, user_svc, mock_jwt_decode):
    mock_jwt_decode["payload"] = {"uid": 42}
    user_svc._raises = RuntimeError("error getting user")

    with pytest.raises(HTTPException) as ei:
        await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)
    assert ei.value.status_code == status.HTTP_401_UNAUTHORIZED

    # user_srv should have been called since attempted
    assert user_svc.get_user_calls == [{"uid": 42}]


# TC-AUTH-GCU-006: User service returns no found user
@pytest.mark.anyio
async def test_get_current_user_not_found(token_credentials, settings, user_svc, mock_jwt_decode):
    mock_jwt_decode["payload"] = {"uid": 999999}
    
    with pytest.raises(HTTPException) as ei:
        await get_current_user(token=token_credentials, settings=settings, user_svc=user_svc)
    assert ei.value.status_code == status.HTTP_401_UNAUTHORIZED

    assert user_svc.get_user_calls == [{"uid": 999999}]