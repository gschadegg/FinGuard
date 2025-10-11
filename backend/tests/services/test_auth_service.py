import pytest
from types import SimpleNamespace
from app.domain.entities import UserEntity
from app.domain.errors import ConflictError, UnauthorizedError

from app.auth_settings import AuthSettings
from app.services.auth_service import AuthService
from app.services.auth_service import pwd_context as _pwd_context_module

import jwt as _jwt_module


class MockUserRepo:
    def __init__(self):
        self._by_email = {}      
        self._by_email_with_hash = {} 
        self._add_return = None

        # get by email calls (no hash)
        self.get_by_email_calls = []

        # get by email with hash called
        self._get_by_email_calls = []
        self.add_calls = []

    async def get_by_email(self, email: str):
        self.get_by_email_calls.append({"email": email})
        return self._by_email.get(email)

    async def _get_by_email(self, email: str):
        self._get_by_email_calls.append({"email": email})
        return self._by_email_with_hash.get(email)

    async def add(self, user_entity: UserEntity, password_hash: str):
        self.add_calls.append({"user": user_entity, "password_hash": password_hash})
        return self._add_return


class MockAuthSettings(AuthSettings):
    def __init__(self):
        self.SECRET_KEY = "secretKey"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MIN = 15

@pytest.fixture
def svc(monkeypatch):
    user_repo = MockUserRepo()
    settings = MockAuthSettings()

    return AuthService(user_repo=user_repo, settings=settings)



@pytest.fixture
def mock_pwd_hash_verify(monkeypatch):

    state = {"hash_result": "$hash$", "verify_result": True}

    def fake_hash(password: str) -> str:
        return state["hash_result"]

    def fake_verify(password: str, pass_hash: str) -> bool:
        return state["verify_result"]

    monkeypatch.setattr(_pwd_context_module, "hash", fake_hash)
    monkeypatch.setattr(_pwd_context_module, "verify", fake_verify)
    return state


@pytest.fixture
def mock_jwt_encode(monkeypatch):
    calls = {"payload": None, "key": None, "algorithm": None}

    def fake_encode(payload, key, algorithm=None):
        calls["payload"] = payload
        calls["key"] = key
        calls["algorithm"] = algorithm
        return "token1"
    
    monkeypatch.setattr(_jwt_module, "encode", fake_encode)
    return calls






############################
# register Tests
############################

# TC-AUTH-REG-001: Base scenario creating new user successfully
@pytest.mark.anyio
async def test_register_user_base(svc, mock_pwd_hash_verify, mock_jwt_encode):
    svc.user_repo._by_email["new@email.com"] = None
    created_row = UserEntity(id=42, email="new@email.com", name="NewUser")
    svc.user_repo._add_return = created_row

    # registers test user
    user, token = await svc.register(email="new@email.com", name="NewUser", password="pw")

    # check that there is a user object
    assert isinstance(user, UserEntity)
    assert (user.id, user.email, user.name) == (42, "new@email.com", "NewUser")
    assert token == "token1"

    # checking that the get by email and add user functions are called 
    assert svc.user_repo.get_by_email_calls == [{"email": "new@email.com"}]
    assert len(svc.user_repo.add_calls) == 1
    add_call = svc.user_repo.add_calls[0]
    assert isinstance(add_call["user"], UserEntity)

    assert add_call["user"].email == "new@email.com" and add_call["user"].name == "NewUser"
    assert isinstance(add_call["password_hash"], str) and add_call["password_hash"] == "$hash$"

    # checks on payload to jwt encode are the proper settings
    p = mock_jwt_encode["payload"]
    assert p["sub"] == "new@email.com" and p["uid"] == 42
    assert isinstance(p["iat"], int) and isinstance(p["exp"], int)
    assert p["exp"] - p["iat"] == svc.settings.ACCESS_TOKEN_EXPIRE_MIN * 60
    assert mock_jwt_encode["key"] == svc.settings.SECRET_KEY
    assert mock_jwt_encode["algorithm"] == svc.settings.ALGORITHM


# TC-AUTH-REG-002: Register user but account with email exists, should raise ConflictError
@pytest.mark.anyio
async def test_register_user_email_exists(svc):
    svc.user_repo._by_email["taken@email.com"] = SimpleNamespace(id=9, email="taken@email.com", name="Taken")

    with pytest.raises(ConflictError, match="Email already exists"):
        await svc.register(email="taken@email.com", name="UserName", password="pw")

    assert svc.user_repo.get_by_email_calls == [{"email": "taken@email.com"}]
    assert len(svc.user_repo.add_calls) == 0



############################
# login Tests
############################

# TC-AUTH-LOGIN-001: Base scenario login user and returns auth token
@pytest.mark.anyio
async def test_login_base(svc, mock_pwd_hash_verify, mock_jwt_encode):
    svc.user_repo._by_email_with_hash["user@email.com"] = SimpleNamespace(
        id=42, email="user@email.com", name="User", password_hash="$bcrypt-hash..."
    )

    mock_pwd_hash_verify["verify_result"] = True

    #running login with mocked user
    user, token = await svc.login(email="user@email.com", password="pw123")

    # checking that user object returned with proper data
    assert isinstance(user, UserEntity)
    assert (user.id, user.email, user.name) == (42, "user@email.com", "User")
    assert token == "token1"

    # check the get by email func was called
    assert svc.user_repo._get_by_email_calls == [{"email": "user@email.com"}]

    # check the jwt encoded has the proper payload
    p = mock_jwt_encode["payload"]
    assert p["sub"] == "user@email.com" and p["uid"] == 42
    assert isinstance(p["iat"], int) and isinstance(p["exp"], int)


# TC-AUTH-LOGIN-002: Login with unknown email
@pytest.mark.anyio
async def test_login_unknown_email(svc, mock_pwd_hash_verify, mock_jwt_encode):
    svc.user_repo._by_email_with_hash["missing@email.com"] = None

    with pytest.raises(UnauthorizedError, match="Invalid email or password"):
        await svc.login(email="missing@email.com", password="pw")

    assert svc.user_repo._get_by_email_calls == [{"email": "missing@email.com"}]

    # check that the jwt encoding wasnt called/ there was no created payload since user wasnt found
    assert mock_jwt_encode["payload"] is None


# TC-AUTH-LOGIN-003: Login with an incorrect password
@pytest.mark.anyio
async def test_login_incorrect_password_raises(svc, mock_pwd_hash_verify, mock_jwt_encode):
    svc.user_repo._by_email_with_hash["user@email.com"] = SimpleNamespace(
        id=42, email="user@email.com", name="User", password_hash="$bcrypt-hash..."
    )
    mock_pwd_hash_verify["verify_result"] = False

    with pytest.raises(UnauthorizedError, match="Invalid email or password"):
        await svc.login(email="user@email.com", password="badpw")

    assert svc.user_repo._get_by_email_calls == [{"email": "user@email.com"}]
    # jwt not called
    assert mock_jwt_encode["payload"] is None


# TC-AUTH-LOGIN-004: Login doesn't reveal password hash
@pytest.mark.anyio
async def test_login_row_to_domain_mapping(svc, mock_pwd_hash_verify, mock_jwt_encode):
    svc.user_repo._by_email_with_hash["no-hash@email.com"] = SimpleNamespace(
        id=11, email="no-hash@email.com", name="UserName", password_hash="pw_hash"
    )

    mock_pwd_hash_verify["verify_result"] = True
    user, _ = await svc.login(email="no-hash@email.com", password="pw")
    assert isinstance(user, UserEntity)
    assert (user.id, user.email, user.name) == (11, "no-hash@email.com", "UserName")