import pytest
from httpx import AsyncClient

from .utils import create_client

pytestmark = [pytest.mark.asyncio(loop_scope="session"), pytest.mark.usefixtures("clean_db")]


async def test_client_crud_flow(http_client: AsyncClient) -> None:
    payload = {"name": "Alice", "email": "alice@example.com", "phone": "+123456789"}
    create_resp = await http_client.post("/clients", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    client_id = created["id"]

    get_resp = await http_client.get(f"/clients/{client_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["name"] == "Alice"
    assert fetched["email"] == "alice@example.com"
    assert fetched["phone"] == "+123456789"

    update_resp = await http_client.put(
        f"/clients/{client_id}", json={"name": "Alice Updated", "phone": "+987654321"}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "Alice Updated"
    assert updated["phone"] == "+987654321"
    assert updated["email"] == "alice@example.com"

    delete_resp = await http_client.delete(f"/clients/{client_id}")
    assert delete_resp.status_code == 204

    not_found_resp = await http_client.get(f"/clients/{client_id}")
    assert not_found_resp.status_code == 404

