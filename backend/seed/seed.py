import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db.engine import SessionLocal
from infrastructure.db.models.user import User


USER_SAMPLE = [
    {"email": "a@b.com", "name": "Alice"},
    {"email": "j@d.com", "name": "John"},
]

async def main():
    async with SessionLocal() as db:
        for row in USER_SAMPLE:
            exists = await db.execute(select(User).where(User.email == row["email"]))
            if not exists.scalar_one_or_none():
                db.add(User(**row))
        await db.commit()

if __name__ == "__main__":
    # this may needs to be done for any asyncio.run because issues with windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())