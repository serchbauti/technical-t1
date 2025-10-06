import os
from typing import Iterator

import anyio
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.infrastructure.db.models import ClientDoc, CardDoc, ChargeDoc
from app.main import app


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--use-test-mongo", action="store_true", default=True)


def _get_client(uri: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(uri)


async def _drop_database(uri: str) -> None:
    client = _get_client(uri)
    try:
        db = client.get_default_database()
        if db is not None:
            await client.drop_database(db.name)
    finally:
        client.close()


async def _clear_collections(uri: str) -> None:
    client = _get_client(uri)
    try:
        db = client.get_default_database()
        if db is None:
            return
        await db[ClientDoc.get_settings().name].delete_many({})
        await db[CardDoc.get_settings().name].delete_many({})
        await db[ChargeDoc.get_settings().name].delete_many({})
    finally:
        client.close()


@pytest.fixture(scope="session", autouse=True)
def configure_settings(pytestconfig: pytest.Config) -> Iterator[None]:
    if pytestconfig.getoption("--use-test-mongo"):
        test_uri = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/t1db_test")
        settings.mongodb_uri = test_uri
    anyio.run(_drop_database, settings.mongodb_uri)
    yield
    anyio.run(_drop_database, settings.mongodb_uri)


@pytest.fixture(scope="session")
def test_client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_db() -> Iterator[None]:
    anyio.run(_clear_collections, settings.mongodb_uri)
    yield
    anyio.run(_clear_collections, settings.mongodb_uri)
