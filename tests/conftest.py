import os
from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.infrastructure.db.mongo import init_mongo, close_mongo
from app.infrastructure.db.models import ClientDoc, CardDoc, ChargeDoc
from app.main import app


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--use-test-mongo", action="store_true", default=True)


@pytest.fixture(scope="session", autouse=True)
async def configure_settings(pytestconfig: pytest.Config) -> AsyncIterator[None]:
    if pytestconfig.getoption("--use-test-mongo"):
        test_uri = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/t1db_test")
        settings.mongodb_uri = test_uri
    await _drop_database(settings.mongodb_uri)
    yield
    await _drop_database(settings.mongodb_uri)


async def _drop_database(uri: str) -> None:
    client = AsyncIOMotorClient(uri)
    try:
        db = client.get_default_database()
        if db is not None:
            await client.drop_database(db.name)
    finally:
        client.close()


async def _clear_collections(uri: str) -> None:
    client = AsyncIOMotorClient(uri)
    try:
        db = client.get_default_database()
        if db is None:
            return
        for name in (
            ClientDoc.get_settings().name,
            CardDoc.get_settings().name,
            ChargeDoc.get_settings().name,
        ):
            await db[name].delete_many({})
    finally:
        client.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_database() -> AsyncIterator[None]:
    await init_mongo()
    yield
    await close_mongo()


@pytest.fixture(scope="session")
async def http_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(autouse=True)
async def clean_db() -> AsyncIterator[None]:
    await _clear_collections(settings.mongodb_uri)
    yield
    await _clear_collections(settings.mongodb_uri)


