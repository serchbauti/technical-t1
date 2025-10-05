from __future__ import annotations

from typing import Sequence, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.infrastructure.db.models import ClienteDoc, TarjetaDoc, ChargeDoc

_client: Optional[AsyncIOMotorClient] = None


async def init_mongo(models: Sequence[type] = (ClienteDoc, TarjetaDoc, ChargeDoc)) -> None:
    """
    Create a singleton Motor client and initialize Beanie with the provided Documents.
    The database name should be present in MONGODB_URI (e.g., mongodb://host:27017/t1db).
    """
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)

    db = _client.get_default_database()  # derives DB name from the URI
    await init_beanie(database=db, document_models=list(models))


async def get_client() -> AsyncIOMotorClient:
    """Return the singleton Motor client (initialized on startup)."""
    assert _client is not None, "Mongo client not initialized"
    return _client


async def close_mongo() -> None:
    """Close the Mongo client gracefully (optional: call on shutdown)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
