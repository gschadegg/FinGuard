from typing import Optional

from app.db_interfaces import AccountRepo, ConnectionItemRepo
from app.domain.entities import (
    AccountEntity,
    ConnectionItemEntity,
    FullAccountEntity,
    PlaidAccountViewEntity,
    PlaidBalancesEntity,
)
from app.domain.errors import NotFoundError
from app.services.plaid_service import PlaidService


class AccountService:
    def __init__(self, account_repo: AccountRepo, 
                 connection_item_repo: ConnectionItemRepo, plaid: PlaidService):
        self.account_repo = account_repo
        self.connection_repo = connection_item_repo
        self.plaid_svc = plaid

    async def list_all_user_accounts(self, user_id, selected) -> list[FullAccountEntity]:
        accounts = await self.account_repo.list_by_user_id(user_id, selected)

        if not accounts:
            raise NotFoundError("No Accounts found for this User")
        
        by_item: dict[int, list[AccountEntity]] = {}
        for a in accounts:
            by_item.setdefault(a.item_id, []).append(a)



        accounts_list: list[FullAccountEntity] = []
        for item_id, group in by_item.items():
            plaid_ids = [a.plaid_account_id for a in group]
            plaid_map = await self.plaid_svc.get_accounts(item_id=item_id, account_ids=plaid_ids)
            item = await self.connection_repo.get_by_id(item_id)
            for a in group:
                accounts_list.append(self._merge_plaid_data(a, 
                                                            plaid_map.get(a.plaid_account_id), 
                                                            item))

        return accounts_list



    async def get_account_by_id(self, account_id, plaid_account_id, user_id) -> FullAccountEntity:
        account = await self.account_repo.get_one(account_id=account_id, 
                                                  plaid_account_id=plaid_account_id)

        if not account:
            raise NotFoundError("Account not found")
        
        item = await self.connection_repo.get_by_id(account.item_id)
        if not item or item.user_id != user_id:
            raise NotFoundError("Account not found")
        
        
        
        plaid_map = await self.plaid_svc.get_accounts(
            item_id=account.item_id, 
            account_ids=[account.plaid_account_id]
        )
        item = await self.connection_repo.get_by_id(account.item_id)

        return self._merge_plaid_data(account, plaid_map.get(account.plaid_account_id), item)

    def _merge_plaid_data(
        self, 
        account: AccountEntity, 
        plaid_account: Optional[dict], 
        item: Optional[ConnectionItemEntity]
    ) -> FullAccountEntity:

        merged_account = FullAccountEntity(
            id=account.id, item_id=account.item_id, plaid_account_id=account.plaid_account_id,
            name=account.name, 
            mask=account.mask, 
            type=account.type, 
            subtype=account.subtype, 
            selected=account.selected,
            institution_id=getattr(account, "institution_id", None) or 
                (item.institution_id if item else None),
            institution_name=getattr(account, "institution_name", None) or 
                (item.institution_name if item else None),
            plaid=None
        )
        if not plaid_account:
            return merged_account

        merged_account.plaid = PlaidAccountViewEntity(
            account_id=plaid_account["account_id"],
            name=plaid_account.get("name"),
            official_name=plaid_account.get("official_name"),
            mask=plaid_account.get("mask"),
            type=plaid_account.get("type"),
            subtype=plaid_account.get("subtype"),
            verification_status=plaid_account.get("verification_status"),
            balances=
                PlaidBalancesEntity(**plaid_account.get("balances", {})) 
                    if plaid_account.get("balances") 
                    else None,
        )
        return merged_account