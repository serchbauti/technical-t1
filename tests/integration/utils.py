from __future__ import annotations

import random
from typing import Any, Dict, Iterable

from httpx import AsyncClient

from app.domain.rules.luhn import generate_luhn


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
    while True:
        body = [random.randint(0, 9) for _ in range(body_length)]
        digits = [int(c) for c in bin_prefix] + body + [int(last4[0]), int(last4[1]), int(last4[2])]
        check_digit = _luhn_check_digit(digits)
        if check_digit == int(last4[3]):
            digits.append(check_digit)
            return "".join(str(d) for d in digits)


def create_pan(bin_prefix: str = "411111") -> str:
    return generate_luhn(bin_prefix)


async def create_client(http_client: AsyncClient, **overrides: Any) -> Dict[str, Any]:
    payload = {"name": "Test Client", "email": "client@example.com", "phone": "+1000000000"}
    payload.update(overrides)
    response = await http_client.post("/clients", json=payload)
    response.raise_for_status()
    return response.json()


async def create_card(
    http_client: AsyncClient,
    client_id: str,
    pan: str | None = None,
) -> Dict[str, Any]:
    card_pan = pan or create_pan()
    response = await http_client.post("/cards", json={"client_id": client_id, "pan": card_pan})
    response.raise_for_status()
    return response.json()


async def create_charge(
    http_client: AsyncClient,
    client_id: str,
    card_id: str,
    amount: float,
    request_id: str | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"client_id": client_id, "card_id": card_id, "amount": amount}
    if request_id is not None:
        payload["request_id"] = request_id
    response = await http_client.post("/charges", json=payload)
    response.raise_for_status()
    return response.json()

