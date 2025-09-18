from contextlib import asynccontextmanager
from fastapi import Depends
from .engine import engine, SessionLocal

@asynccontextmanager
async def lifespan(app):
    yield
    await engine.dispose()

async def get_db():
    async with SessionLocal() as session:
        yield session