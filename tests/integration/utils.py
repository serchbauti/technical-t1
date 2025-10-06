from __future__ import annotations

import random
from typing import Any, Dict, Iterable

from fastapi.testclient import TestClient

from app.domain.rules.luhn import generate_luhn, is_valid_luhn


def _luhn_check_digit(digits: Iterable[int]) -> int:
    digits_list = list(digits)
    parity = len(digits_list) % 2
    total = 0
    for idx, digit in enumerate(digits_list):
        d = digit
        if idx % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - (total % 10)) % 10


def generate_pan_with_last4(last4: str, bin_prefix: str = "411111", length: int = 16) -> str:
    if len(last4) != 4 or not last4.isdigit():
        raise ValueError("last4 must be exactly 4 digits")
    if len(bin_prefix) >= length - 4:
        raise ValueError("bin_prefix must leave room for body and last4 digits")

    body_length = length - len(bin_prefix) - 4
    attempts = 0
    while attempts < 10000:
        body = ''.join(str(random.randint(0, 9)) for _ in range(body_length))
        candidate = f"{bin_prefix}{body}{last4}"
        if is_valid_luhn(candidate):
            return candidate
        attempts += 1
    raise ValueError("could not generate a Luhn-valid PAN with the requested last4")


def create_pan(bin_prefix: str = "411111") -> str:
    return generate_luhn(bin_prefix)


def create_client(client: TestClient, **overrides: Any) -> Dict[str, Any]:
    payload = {"name": "Test Client", "email": "client@example.com", "phone": "+1000000000"}
    payload.update(overrides)
    response = client.post("/clients", json=payload)
    response.raise_for_status()
    return response.json()


def create_card(
    client: TestClient,
    client_id: str,
    pan: str | None = None,
) -> Dict[str, Any]:
    card_pan = pan or create_pan()
    response = client.post("/cards", json={"client_id": client_id, "pan": card_pan})
    response.raise_for_status()
    return response.json()


def create_charge(
    client: TestClient,
    client_id: str,
    card_id: str,
    amount: float,
    request_id: str | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"client_id": client_id, "card_id": card_id, "amount": amount}
    if request_id is not None:
        payload["request_id"] = request_id
    response = client.post("/charges", json=payload)
    response.raise_for_status()
    return response.json()
