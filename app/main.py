from fastapi import FastAPI
from app.infrastructure.db.mongo import init_mongo
from app.http.routers import health as health_router
from app.http.routers import client as client_router
from app.http.routers import card as card_router
from app.http.routers import charge as charge_router

app = FastAPI(title="T1 Cobros API (DDD)")

@app.on_event("startup")
async def on_startup():
    # Initialize Mongo + Beanie registering Document models defined in infrastructure/db/models.py
    await init_mongo()

# Public routers
app.include_router(health_router.router)
app.include_router(client_router.router)
app.include_router(card_router.router)
app.include_router(charge_router.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"hello": "world", "docs": "/docs", "health": "/health"}
    
