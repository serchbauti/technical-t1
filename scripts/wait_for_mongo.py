#!/usr/bin/env python3
from __future__ import annotations

import os
import time

from pymongo import MongoClient
from pymongo.errors import PyMongoError


def wait_for_mongo(timeout: int = 60, poll_interval: float = 1.0) -> None:
    uri = os.getenv("TEST_MONGODB_URI", "mongodb://mongo:27017/t1db_test")
    deadline = time.time() + timeout

    while True:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=int(poll_interval * 1000))
            client.admin.command("ping")
            client.close()
            return
        except (PyMongoError, OSError):
            if time.time() >= deadline:
                raise
            time.sleep(poll_interval)


if __name__ == "__main__":
    wait_for_mongo()
