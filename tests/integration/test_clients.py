import pytest

pytestmark = [pytest.mark.usefixtures("clean_db")]


def test_client_crud_flow(test_client) -> None:
    payload = {"name": "Alice", "email": "alice@example.com", "phone": "+123456789"}
    create_resp = test_client.post("/clients", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    client_id = created["id"]

    get_resp = test_client.get(f"/clients/{client_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["name"] == "Alice"
    assert fetched["email"] == "alice@example.com"
    assert fetched["phone"] == "+123456789"

    update_resp = test_client.put(
        f"/clients/{client_id}", json={"name": "Alice Updated", "phone": "+987654321"}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "Alice Updated"
    assert updated["phone"] == "+987654321"
    assert updated["email"] == "alice@example.com"

    delete_resp = test_client.delete(f"/clients/{client_id}")
    assert delete_resp.status_code == 204

    not_found_resp = test_client.get(f"/clients/{client_id}")
    assert not_found_resp.status_code == 404

