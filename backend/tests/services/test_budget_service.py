import pytest
from decimal import Decimal
from datetime import date
from types import SimpleNamespace
from fastapi import HTTPException

from app.services.budget_service import BudgetService


class MockBudgetCategoryRepo:
    def __init__(self):
        self._by_id = {}
        self._by_user_and_name = {}
        self.created = []
        self.updated = []
        self.deleted = []
        self.listed_for = []

    async def list_by_user(self, user_id: int, start_date=None, end_date=None):
        self.listed_for.append((user_id, start_date, end_date))

        return [e for e in self._by_id.values() if e.user_id == user_id]

    async def get_by_name(self, user_id: int, name: str):
        key = (user_id, name.lower())
        cid = self._by_user_and_name.get(key)
        return self._by_id.get(cid)

    async def create(self, user_id: int, name: str, allotted_amount, group: str):
        new_id = (max(self._by_id.keys()) + 1) if self._by_id else 1

        entity = SimpleNamespace(
            id=new_id,
            user_id=user_id,
            name=name,
            allotted_amount=Decimal(allotted_amount),
            group=group,
        )

        self._by_id[new_id] = entity
        self._by_user_and_name[(user_id, name.lower())] = new_id

        self.created.append((user_id, name, Decimal(allotted_amount), group))

        return entity

    async def update(self, user_id: int, category_id: int, patch: dict):
        entity = self._by_id.get(category_id)

        if not entity or entity.user_id != user_id:
            raise ValueError("not found")
        
        for k, v in patch.items():

            setattr(entity, k, v)
            if k == "name":
                for key, categoryId in list(self._by_user_and_name.items()):
                    if categoryId == category_id:
                        del self._by_user_and_name[key]
                self._by_user_and_name[(user_id, v.lower())] = category_id
        self.updated.append((user_id, category_id, dict(patch)))


        return entity

    async def delete(self, user_id: int, category_id: int):
        entity = self._by_id.get(category_id)

        if not entity or entity.user_id != user_id:
            raise Exception("not found")

        self.deleted.append((user_id, category_id))
        del self._by_id[category_id]

        for key, cid in list(self._by_user_and_name.items()):
            if cid == category_id:
                del self._by_user_and_name[key]



@pytest.fixture
def svc():
    repo = MockBudgetCategoryRepo()
    return BudgetService(budget_repo=repo)


def _createCategory(repo: MockBudgetCategoryRepo, *, id=1, user_id=7, name="Groceries",
          amt=Decimal("300.00"), group="Expenses"):
    

    entity = SimpleNamespace(id=id, user_id=user_id, name=name,
                          allotted_amount=Decimal(amt), group=group)
    
    repo._by_id[id] = entity
    repo._by_user_and_name[(user_id, name.lower())] = id

    return entity


############################
# crud budget tests
############################

# TC-BC-LIST-001: Lists user categories for specific month and year
@pytest.mark.anyio
async def test_list_categories_by_user(svc):
    repo = svc.budget_repo


    _createCategory(repo, id=1, user_id=10, name="Rent", amt="1200.00", group="Expenses")
    _createCategory(repo, id=2, user_id=10, name="Movies", amt="50.00", group="Entertainment")
    _createCategory(repo, id=3, user_id=99, name="OtherUser", amt="1.00", group="Savings")

    list = await svc.list_categories(user_id=10, year=2024, month=5)


    assert [category.name for category in list] == ["Rent", "Movies"]

    assert len(repo.listed_for) == 1
    user_id, start_date, end_date = repo.listed_for[0]

    assert user_id == 10
    assert start_date.year == 2024
    assert start_date.month == 5
    assert end_date.year == 2024
    assert end_date.month == 6
    assert start_date <= end_date


# TC-BC-LIST-002: List categories defaulting to current month and year
@pytest.mark.anyio
async def test_list_categories_default_month(svc, monkeypatch):
    repo = svc.budget_repo

    _createCategory(repo, id=1, user_id=10, name="Rent", amt="1200.00", group="Expenses")

    from app.services import budget_service

    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 11, 15)

    monkeypatch.setattr(budget_service, "date", FixedDate)


    result = await svc.list_categories(user_id=10)

    assert [category.name for category in result] == ["Rent"]

    assert len(repo.listed_for) == 1
    user_id, start_date, end_date = repo.listed_for[0]

    assert user_id == 10
    assert start_date.year == 2025
    assert start_date.month == 11
    assert end_date.year == 2025
    assert end_date.month == 12
    assert start_date <= end_date


# TC-BC-LIST-003: List categories with default month but year passed by request
@pytest.mark.anyio
async def test_list_categories_pass_year(svc, monkeypatch):
    repo = svc.budget_repo
    _createCategory(repo, id=1, user_id=10, name="Rent", amt="1200.00", group="Expenses")

    from app.services import budget_service

    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2023, 11, 15)

    monkeypatch.setattr(budget_service, "date", FixedDate)


    result = await svc.list_categories(user_id=10, year=2022)

    assert [category.name for category in result] == ["Rent"]

    assert len(repo.listed_for) == 1
    user_id, start_date, end_date = repo.listed_for[0]

    assert user_id == 10
    assert start_date.year == 2022
    assert end_date.year == 2022
    assert start_date.month == 11
    assert end_date.month == 12
    assert start_date <= end_date


# TC-BC-CREATE-001: base scenario, create category
@pytest.mark.anyio
async def test_create_category_base(svc):
    repo = svc.budget_repo


    entity = await svc.create_category(
        user_id=7, name="Groceries", allotted_amount=Decimal("250.00"), group="Expenses"
    )
    assert entity.name == "Groceries"
    assert entity.group == "Expenses"

    assert entity.allotted_amount == Decimal("250.00")
    assert repo.created == [(7, "Groceries", Decimal("250.00"), "Expenses")]



# TC-BC-CREATE-002: duplicate name
@pytest.mark.anyio
async def test_create_category_name_duplicate(svc):
    repo = svc.budget_repo
    _createCategory(repo, id=1, user_id=7, name="Groceries", amt="200.00", group="Expenses")

    with pytest.raises(HTTPException) as exception:
        await svc.create_category(7, "Groceries", Decimal("300.00"), "Expenses")

    assert exception.value.status_code == 409
    assert repo.created == []


# TC-BC-CREATE-003: invalid category group
@pytest.mark.anyio
async def test_create_category_invalid_group(svc):
    repo = svc.budget_repo

    with pytest.raises(HTTPException) as exception:
        await svc.create_category(7, "Travel", Decimal("500.00"), "InvalidGroup")

    assert exception.value.status_code == 422
    assert repo.created == []




# TC-BC-UPDATE-001: base scenario, update of name, amount, and group
@pytest.mark.anyio
async def test_update_category_base(svc):
    repo = svc.budget_repo
    _createCategory(repo, id=2, user_id=7, name="Old", amt="10.00", group="Savings")

    ent = await svc.update_category(
        user_id=7,
        category_id=2,
        name="NewName",
        allotted_amount=Decimal("99.99"),
        group="Expenses",
    )

    assert ent.name == "NewName"
    assert ent.allotted_amount == Decimal("99.99")

    assert ent.group == "Expenses"
    assert repo.updated == [(7, 2, {"name": "NewName", "allotted_amount": Decimal("99.99"), "group": "Expenses"})]


# TC-BC-UPDATE-002: update name to existing category name
@pytest.mark.anyio
async def test_update_category_name_duplicate(svc):
    repo = svc.budget_repo

    _createCategory(repo, id=1, user_id=7, name="Groceries", amt="200.00", group="Expenses")
    _createCategory(repo, id=2, user_id=7, name="Dining", amt="150.00", group="Expenses")

    with pytest.raises(HTTPException) as exception:

        await svc.update_category(
            user_id=7, category_id=2, name="Groceries",
            allotted_amount=None, group=None
        )

    assert exception.value.status_code == 409
    assert repo.updated == []



# TC-BC-UPDATE-003: updating to invalid group
@pytest.mark.anyio
async def test_update_category_invalid_group(svc):
    repo = svc.budget_repo

    _createCategory(repo, id=5, user_id=7, name="Pets", amt="30.00", group="Expenses")

    with pytest.raises(HTTPException) as exception:
        await svc.update_category(
            user_id=7, category_id=5, name=None, allotted_amount=None, group="NotAGroup"
        )


    assert exception.value.status_code == 422
    assert repo.updated == []


# TC-BC-UPDATE-004: updating category doesnt exist
@pytest.mark.anyio
async def test_update_category_not_found(svc):

    with pytest.raises(HTTPException) as exception:
        await svc.update_category(
            user_id=7, category_id=999, name="Pets", allotted_amount=None, group=None
        )

    assert exception.value.status_code == 404




# TC-BC-DELETE-001: base scenario, delete category
@pytest.mark.anyio
async def test_delete_category_base(svc):
    repo = svc.budget_repo


    _createCategory(repo, id=11, user_id=7, name="Pets", amt="1.00", group="Expenses")
    out = await svc.delete_category(7, 11)

    assert out == {"ok": True}
    assert repo.deleted == [(7, 11)]

    assert 11 not in repo._by_id


# TC-BC-DELETE-002: delete category doesn't exist
@pytest.mark.anyio
async def test_delete_category_not_found(svc):
    
    with pytest.raises(HTTPException) as exception:
        await svc.delete_category(7, 12345)

    assert exception.value.status_code == 404
