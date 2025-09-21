import pytest
from typing import Optional, Sequence, List
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock
from app.services.plaid_service import PlaidService
from app.domain.entities import UserEntity
from app.domain.errors import NotFoundError, ConflictError
from fastapi import HTTPException

class MockAccountRepo:
    def __init__(self):
        self.rows: List[UserEntity] = []
        self._id = 0

class MockConnectionItemRepo:
    def __init__(self):
        self.rows: List[UserEntity] = []
        self._id = 0


@pytest.fixture
def mock_plaid_client(monkeypatch):
    client = SimpleNamespace(link_token_create=Mock())

    monkeypatch.setattr("app.services.plaid_service.plaid_client", client)
    return client



# Test Case TC-007: create_link_token BASE scenario
@pytest.mark.anyio
async def test_create_link_token_base(mock_plaid_client):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo()) 

    mock_plaid_client.link_token_create.return_value = SimpleNamespace(
        to_dict=lambda: {"link_token": "link-token-sandbox-123"}
    )

    result = await svc.create_link_token(user_id="user-123")

    assert result == {"link_token": "link-token-sandbox-123"}
    assert mock_plaid_client.link_token_create.call_count == 1



# Test Case TC-008: create_link_token Plaid throws error scenario
@pytest.mark.anyio
async def test_create_link_token_plaid_error(mock_plaid_client):
    svc = PlaidService(account_repo=MockAccountRepo(), connection_item_repo=MockConnectionItemRepo()) 

    mock_plaid_client.link_token_create.side_effect = RuntimeError("Plaid Error")

    with pytest.raises(HTTPException) as ei:
        await svc.create_link_token(user_id="user-123")

    assert ei.value.status_code == 500
