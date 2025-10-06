from __future__ import annotations

import pytest
from httpx import AsyncClient

from .utils import create_client, create_card, create_pan, generate_pan_with_last4

pytestmark = [pytest.mark.asyncio(loop_scope="session"), pytest.mark.usefixtures("clean_db")]


async def test_card_crud_flow(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    client_id = client["id"]

    pan = create_pan()
    card = await create_card(http_client, client_id=client_id, pan=pan)
    card_id = card["id"]

    get_resp = await http_client.get(f"/cards/{card_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["client_id"] == client_id
    assert fetched["pan_masked"].endswith(fetched["last4"])
    assert set(fetched["pan_masked"][:-4]) == {"*"}

    new_last4 = "4242"
    update_payload = {"bin": "555555", "last4": new_last4}
    update_resp = await http_client.put(f"/cards/{card_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["bin"] == "555555"
    assert updated["last4"] == new_last4
    assert updated["pan_masked"].endswith(new_last4)
    assert set(updated["pan_masked"][:-4]) == {"*"}

    delete_resp = await http_client.delete(f"/cards/{card_id}")
    assert delete_resp.status_code == 204

    not_found_resp = await http_client.get(f"/cards/{card_id}")
    assert not_found_resp.status_code == 404


async def test_card_creation_rejects_invalid_pan(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    invalid_payload = {"client_id": client["id"], "pan": "123456789012"}
    response = await http_client.post("/cards", json=invalid_payload)
    assert response.status_code == 422


async def test_card_pan_masking_forced_last4(http_client: AsyncClient) -> None:
    client = await create_client(http_client)
    pan = generate_pan_with_last4("7777")
    card = await create_card(http_client, client_id=client["id"], pan=pan)

    assert card["last4"] == "7777"
    assert card["pan_masked"].endswith("7777")
    assert set(card["pan_masked"][:-4]) == {"*"}

