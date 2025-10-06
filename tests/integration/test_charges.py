from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

import pytest
from httpx import AsyncClient

from .utils import (
    create_card,
    create_charge,
    create_client,
    create_pan,
    generate_pan_with_last4,
)

pytestmark = [pytest.mark.asyncio(loop_scope="session"), pytest.mark.usefixtures("clean_db")]


async def test_charge_approval_flow(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    card = await create_card(http_client, client_id=client["id"], pan=create_pan())

    charge = await create_charge(http_client, client_id=client["id"], card_id=card["id"], amount=200.0)
    assert charge["status"] == "approved"
    assert charge["reason_code"] is None

    refund_resp = await http_client.post(f"/charges/{charge['id']}/refund")
    assert refund_resp.status_code == 200
    refunded = refund_resp.json()
    assert refunded["refunded"] is True
    assert refunded["status"] == "approved"
    assert refunded["refunded_at"] is not None

    second_refund = await http_client.post(f"/charges/{charge['id']}/refund")
    assert second_refund.status_code == 409


async def test_charge_declined_by_rules(http_client: AsyncClient) -> None:
    client = await create_client(http_client)

    blocked_card = await create_card(
        http_client,
        client_id=client["id"],
        pan=generate_pan_with_last4("0000"),
    )
    blocked_charge = await create_charge(
        http_client,
        client_id=client["id"],
        card_id=blocked_card["id"],
        amount=100.0,
    )
    assert blocked_charge["status"] == "declined"
    assert blocked_charge["reason_code"] == "SUSPECT_PAN"

    high_amount_card = await create_card(http_client, client_id=client["id"], pan=create_pan())
    high_amount_charge = await create_charge(
        http_client,
        client_id=client["id"],
        card_id=high_amount_card["id"],
        amount=6000.0,
    )
    assert high_amount_charge["status"] == "declined"
    assert high_amount_charge["reason_code"] == "LIMIT_EXCEEDED"


async def test_charge_idempotency(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    card = await create_card(http_client, client_id=client["id"], pan=create_pan())

    request_id = "duplicate-123"
    first = await create_charge(
        http_client,
        client_id=client["id"],
        card_id=card["id"],
        amount=350.0,
        request_id=request_id,
    )

    second_resp = await http_client.post(
        "/charges",
        json={
            "client_id": client["id"],
            "card_id": card["id"],
            "amount": 999.0,
            "request_id": request_id,
        },
    )
    assert second_resp.status_code == 200
    second = second_resp.json()
    assert second["id"] == first["id"]
    assert second["amount"] == first["amount"]


async def test_charge_listing_filters(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    card = await create_card(http_client, client_id=client["id"], pan=create_pan())

    approved_charge = await create_charge(
        http_client,
        client_id=client["id"],
        card_id=card["id"],
        amount=100.0,
    )
    declined_charge = await create_charge(
        http_client,
        client_id=client["id"],
        card_id=card["id"],
        amount=6000.0,
    )

    since = datetime.now(timezone.utc) - timedelta(minutes=5)
    until = datetime.now(timezone.utc) + timedelta(minutes=5)

    all_resp = await http_client.get(f"/charges/{client['id']}")
    assert all_resp.status_code == 200
    all_charges: List[dict] = all_resp.json()
    assert {c["id"] for c in all_charges} == {approved_charge["id"], declined_charge["id"]}

    approved_resp = await http_client.get(
        f"/charges/{client['id']}", params={"status": "approved"}
    )
    approved_only: List[dict] = approved_resp.json()
    assert [c["id"] for c in approved_only] == [approved_charge["id"]]

    declined_resp = await http_client.get(
        f"/charges/{client['id']}", params={"status": "declined"}
    )
    declined_only: List[dict] = declined_resp.json()
    assert [c["id"] for c in declined_only] == [declined_charge["id"]]

    window_resp = await http_client.get(
        f"/charges/{client['id']}",
        params={"since": since.isoformat(), "until": until.isoformat()},
    )
    window_charges: List[dict] = window_resp.json()
    assert {c["id"] for c in window_charges} == {approved_charge["id"], declined_charge["id"]}

    refund_resp = await http_client.post(f"/charges/{approved_charge['id']}/refund")
    assert refund_resp.status_code == 200
    history_resp = await http_client.get(f"/charges/{client['id']}")
    history: List[dict] = history_resp.json()
    refunded = next(item for item in history if item["id"] == approved_charge["id"])
    assert refunded["refunded"] is True
    assert refunded["refunded_at"] is not None
