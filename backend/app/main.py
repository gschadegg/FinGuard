from fastapi import FastAPI, Request
from pydantic import BaseModel
import time

from infrastructure.db.session import lifespan
from app.api.v1.users import router as users_router

app = FastAPI(lifespan=lifespan)

# examples from doc notes
app.include_router(users_router)



#testing example endpoints with how they work in FastAPI
@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


@app.get("/items2/{item_id}")
async def read_item2(item_id: int):
    return {"item_id": item_id}

@app.get("/items3/{item_id}")
async def read_item3(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    return item

# Middle ware example
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
