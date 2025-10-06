from __future__ import annotations

import pytest

from .utils import create_client, create_card, create_pan

pytestmark = [pytest.mark.usefixtures("clean_db")]


def test_card_crud_flow(test_client) -> None:
    client = create_client(test_client)
    client_id = client["id"]

    pan = create_pan()
    card = create_card(test_client, client_id=client_id, pan=pan)
    card_id = card["id"]

    get_resp = test_client.get(f"/cards/{card_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["client_id"] == client_id
    assert fetched["pan_masked"].endswith(fetched["last4"])
    assert set(fetched["pan_masked"][:-4]) == {"*"}

    new_last4 = "4242"
    update_payload = {"bin": "555555", "last4": new_last4}
    update_resp = test_client.put(f"/cards/{card_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["bin"] == "555555"
    assert updated["last4"] == new_last4
    assert updated["pan_masked"].endswith(new_last4)
    assert set(updated["pan_masked"][:-4]) == {"*"}

    delete_resp = test_client.delete(f"/cards/{card_id}")
    assert delete_resp.status_code == 204

    not_found_resp = test_client.get(f"/cards/{card_id}")
    assert not_found_resp.status_code == 404


def test_card_creation_rejects_invalid_pan(test_client) -> None:
    client = create_client(test_client)
    invalid_payload = {"client_id": client["id"], "pan": "123456789012"}
    response = test_client.post("/cards", json=invalid_payload)
    assert response.status_code == 422


def test_card_pan_masking_forced_last4(test_client) -> None:
    client = create_client(test_client)
    pan = create_pan()
    card = create_card(test_client, client_id=client["id"], pan=pan)

    assert card["pan_masked"].endswith(card["last4"])
    assert set(card["pan_masked"][:-4]) == {"*"}

