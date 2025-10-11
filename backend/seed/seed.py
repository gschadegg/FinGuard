import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db.engine import SessionLocal
from infrastructure.db.models.user import User
from app.services.auth_service import AuthService
from infrastructure.db.repos.user_repo import SqlUserRepo
from app.auth_settings import get_auth_settings

USER_SAMPLE = [
    {"email": "a@b.com", "name": "Alice", "password": "DevPass1!"},
    {"email": "j@d.com", "name": "John", "password": "DevPass1!"},
]

async def main():
    settings = get_auth_settings()
    async with SessionLocal() as db:
        user_repo = SqlUserRepo(db)
        auth_srv = AuthService(user_repo=user_repo, settings=settings)
        for row in USER_SAMPLE:
            if await user_repo.get_by_email(row["email"]):
                continue
            await auth_srv.register(
                email=row["email"],
                name=row["name"],
                password=row["password"],
            )
        #     exists = await db.execute(select(User).where(User.email == row["email"]))
        #     if not exists.scalar_one_or_none():
        #         db.add(User(**row))
        # await db.commit()

if __name__ == "__main__":
    # this may needs to be done for any asyncio.run because issues with windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())