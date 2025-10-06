from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.db.mongo import init_mongo, close_mongo
from app.http.routers import card as card_router
from app.http.routers import charge as charge_router
from app.http.routers import client as client_router
from app.http.routers import health as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_mongo()
    try:
        yield
    finally:
        await close_mongo()


app = FastAPI(title="T1 Technical Test API", lifespan=lifespan)


# Public routers
app.include_router(health_router.router)
app.include_router(client_router.router)
app.include_router(card_router.router)
app.include_router(charge_router.router)


@app.get("/", include_in_schema=False)
async def root():
    return {"hello": "world", "docs": "/docs", "health": "/health"}
