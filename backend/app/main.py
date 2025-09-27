
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.v1.plaid import router as plaid_router
from app.api.v1.users import router as users_router
from infrastructure.db.session import lifespan

app = FastAPI(lifespan=lifespan)

# examples from doc notes
app.include_router(users_router)
app.include_router(plaid_router)



# @app.get("/debug/env")
# def debug_env(settings: Settings = Depends(get_settings)):
#     return {
#         "ENV": settings.ENV,
#         "HAS_PLAID_CLIENT_ID": bool(settings.PLAID_CLIENT_ID),
#         "HAS_PLAID_SECRET": bool(settings.PLAID_SECRET),
#         "env_file": settings.model_config.get("env_file"),
#     }

#testing example endpoints with how they work in FastAPI
# @app.get("/health")
# async def health():
#     return {"ok": True}

@app.get("/")
async def root():
    content = jsonable_encoder({"message": "Hello World"})
    return JSONResponse(content=content)

# @app.get("/items/{item_id}")
# async def read_item(item_id):
#     return {"item_id": item_id}


# @app.get("/items2/{item_id}")
# async def read_item2(item_id: int):
#     return {"item_id": item_id}

# @app.get("/items3/{item_id}")
# async def read_item3(item_id: str, q: str | None = None):
#     if q:
#         return {"item_id": item_id, "q": q}
#     return {"item_id": item_id}


# class Item(BaseModel):
#     name: str
#     description: str | None = None
#     price: float
#     tax: float | None = None


# @app.post("/items/")
# async def create_item(item: Item):
#     return item

# # Middle ware example
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.perf_counter()
#     response = await call_next(request)
#     process_time = time.perf_counter() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response
