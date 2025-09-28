
import json
from typing import Dict, Iterable, List, Literal, Optional

import plaid
from fastapi import HTTPException
from plaid import ApiClient, Configuration
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_get_request_options import AccountsGetRequestOptions
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from app.config import get_settings
from app.db_interfaces import AccountRepo, ConnectionItemRepo
from app.domain.entities import ConnectionItemEntity
from app.security.crypto import decrypt, encrypt

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

    async def create_link_token(self, 
                                user_id:int,
                                mode: Literal["create", "update"] = "create",
                                plaid_item_id: Optional[str] = None,
                                ):
        try:
            # Updating a connection
            if mode == "update" or plaid_item_id is not None:
                item = await self.connection_item_repo.get_by_connection_item_id(plaid_item_id)
                
                if not item:
                    raise HTTPException(404, "Account connection not found")
                access_token = decrypt(item.access_token_encrypted)


                req = LinkTokenCreateRequest(
                    user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
                    client_name="FinGuard",
                    products=[Products("auth"), Products("transactions")],
                    country_codes=[CountryCode("US")],
                    language="en",
                    access_token=access_token
                )
                res = plaid_client.link_token_create(req).to_dict()
                return {
                    "ok": True, 
                    "link_token": res["link_token"],
                    "mode": "update",
                    "plaid_item_id": plaid_item_id
                }
            
            # Creating a new connection
            req = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
                client_name="FinGuard",
                products=[Products("auth"), Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            res = plaid_client.link_token_create(req).to_dict()
            return {"ok": True, "link_token": res["link_token"], "mode": "create"}

        except plaid.ApiException as e:
            status = getattr(e, "status", 500) or 500
            try:
                body = json.loads(e.body) if getattr(e, "body", None) else {"error": str(e)}
            except Exception:
                body = {"error": str(e)}
            raise HTTPException(status_code=status, detail=body)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, str(e))


    async def exchange_public_token(
        self, 
        public_token:str,
        user_id: int, 
        selected_accounts: Optional[Iterable[dict]] = None,
        institution: Optional[dict] = None,
        unselect_others: bool = False,
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

            
        except plaid.ApiException as e:
            status = getattr(e, "status", 500) or 500
            try:
                body = json.loads(e.body) if getattr(e, "body", None) else {"error": str(e)}
            except Exception:
                body = {"error": str(e)}
            raise HTTPException(status_code=status, detail=body)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{type(e).__name__}: {e}")

        institution_id = institution.id if institution else None
        institution_name = institution.name if institution else None
        
        # encrypting access token
        token_encrypted = encrypt(access_token)

        # check if the connection for that item already exists
        item = await self.connection_item_repo.get_by_connection_item_id(plaid_item_id)

        mode = "created"
        if item is None:
            # create new connection item
            item = ConnectionItemEntity(
                user_id=user_id,
                plaid_item_id=plaid_item_id,
                access_token_encrypted=token_encrypted,
                institution_id=institution_id,
                institution_name=institution_name
            )
            item = await self.connection_item_repo.add(item)
        else:

            item = await self.connection_item_repo.update(item, token_encrypted, 
                                                          institution_id, institution_name)
            mode = "updated"
        added_accounts = []
        # save the user selected accounts to the db, these are the ones 
        # related to this connection link
        if selected_accounts:
            added_accounts = await self.account_repo.upsert_selected(
                item_id=item.id, 
                selected_accounts=selected_accounts, 
                unselect_others=unselect_others,
                institution_id=institution_id,
                institution_name=institution_name
            )

        return {
            "ok": True,
            "mode": mode,
            "plaid_item_id": plaid_item_id, 
            "connection_item_id": item.id, 
            "added_accounts": added_accounts, 
            "institution": {"id": item.institution_id, "name": item.institution_name},
        }

    async def get_accounts(
        self,
        *,
        access_token: Optional[str] = None,
        item_id: Optional[int] = None,
        account_ids: Optional[List[str]] = None,
    ) -> Dict[str, dict]:


        if not access_token:
            if item_id is None:
                raise ValueError("Provide either Access Token or Connection ID")
            item = await self.connection_item_repo.get_by_id(item_id) 
            if not item:
                return {}
            access_token = decrypt(item.access_token_encrypted)

        try:
            if account_ids:
                req = AccountsGetRequest(
                    access_token=access_token,
                    options=AccountsGetRequestOptions(account_ids=account_ids),
                )
            else:
                req = AccountsGetRequest(access_token=access_token)

            # fetching account specific data from plaid
            res = plaid_client.accounts_get(req).to_dict()
            accounts = res.get("accounts", [])


            return {a["account_id"]: a for a in accounts}
        except plaid.ApiException:
            return {}

  
    async def transactions_sync(self, access_token: str, cursor: str | None) -> dict:
        if TransactionsSyncRequest is None: # weird thing with plaid, just in case
            return {"added": [], "modified": [], "removed": [], 
                    "next_cursor": cursor, "has_more": False}
        
        req_args = {"access_token": access_token, "count": 500}
        if cursor is not None:
            req_args["cursor"] = cursor

        req = TransactionsSyncRequest(**req_args)
        try:
            res = plaid_client.transactions_sync(req).to_dict()
            return {
                "added": res.get("added", []),
                "modified": res.get("modified", []),
                "removed": res.get("removed", []),
                "next_cursor": res.get("next_cursor"),
                "has_more": res.get("has_more", False),
            }
        except plaid.ApiException:
            return {"added": [], "modified": [], "removed": [], 
                    "next_cursor": cursor, "has_more": False}
        