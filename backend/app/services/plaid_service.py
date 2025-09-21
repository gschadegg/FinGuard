
import os, secrets
import plaid
from typing import Optional, Iterable
from plaid.api import plaid_api
from fastapi import HTTPException, status
from plaid import Configuration, ApiClient
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.country_code import CountryCode

from app.db_interfaces import ConnectionItemRepo, AccountRepo

from app.domain.entities import ConnectionItemEntity
from app.security.crypto import encrypt

from app.config import get_settings

settings = get_settings()

configuration = Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": settings.PLAID_CLIENT_ID,
        "secret": settings.PLAID_SECRET
    },
)

plaid_client = plaid_api.PlaidApi(ApiClient(configuration))

class PlaidService:
    def __init__(self, account_repo: AccountRepo, connection_item_repo: ConnectionItemRepo):
        self.account_repo = account_repo
        self.connection_item_repo = connection_item_repo

    async def create_link_token(self, user_id:str):
        try:
            req = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="My App (Sandbox)",
                products=[Products("auth"), Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            res = plaid_client.link_token_create(req).to_dict()
            return res
            #{resp"link_token": resp["link_token"]}
        except Exception as e:
            raise HTTPException(500, str(e))

    async def exchange_public_token(
        self, 
        public_token:str,
        user_id: int, # app’s user id - not plaids ?
        selected_accounts: Optional[Iterable[dict]] = None
        ):
        if not public_token:
            raise HTTPException(status_code=400, detail="public_token is required")

        try:
            # need to exchange public_token to get the plaid access_token and plaid_item_id
            ex = plaid_client.item_public_token_exchange(
                ItemPublicTokenExchangeRequest(public_token=public_token)
            ).to_dict()

            access_token = ex["access_token"]
            plaid_item_id = ex["item_id"]
        except Exception as e:
            # Getting any Plaid error message, need to communicate to FE
            raise HTTPException(status_code=400, detail=f"{type(e).__name__}: {e}")

        # encrypting access token
        token_encrypted = encrypt(access_token)

        # check if the connection for that item already exists
        item = await self.connection_item_repo.get_by_connection_item_id(plaid_item_id)
        if item is None:
            # create new connection item
            item = ConnectionItemEntity(
                user_id=user_id,
                plaid_item_id=plaid_item_id,
                access_token_encrypted=token_encrypted,
            )
            item = await self.connection_item_repo.add(item)
        else:
            # update rotated access token (need to do this if access token has expired, removed, connection has been redone)
            # also need to do this if the enryption key needs to be rotated
            # dont have 'update_access_token' yet, need to create this!
            item = await self.connection_item_repo.update_access_token(item, token_encrypted)

        # save the user selected accounts to the db, these are the ones related to this connection link
        if selected_accounts:
            await self.account_repo.upsert_selected(item_id=item.id, selected_accounts=selected_accounts)

        # want to return info on the connection item and status, think I want to return accounts through a different request?
        return {"ok": True, "plaid_item_id": plaid_item_id, "item_db_id": item.id}
