from __future__ import annotations

import pytest

from app.domain.rules.luhn import derive_bin_last4, generate_luhn, is_valid_luhn, mask_pan

pytestmark = [pytest.mark.usefixtures("clean_db")]


def test_generate_luhn_produces_valid_number() -> None:
    pan = generate_luhn("411111")
    assert len(pan) == 16
    assert is_valid_luhn(pan)


@pytest.mark.parametrize(
    "pan,is_valid",
    [
        ("4111111111111111", True),
        ("4111111111111112", False),
        ("", False),
        ("abcd", False),
    ],
)
def test_is_valid_luhn(pan: str, is_valid: bool) -> None:
    assert is_valid_luhn(pan) is is_valid


def test_mask_pan_preserves_last4() -> None:
    masked = mask_pan("1234567890123456")
    assert masked.endswith("3456")
    assert set(masked[:-4]) == {"*"}


def test_derive_bin_last4() -> None:
    bin_value, last4 = derive_bin_last4("4111111111111111")
    assert bin_value == "411111"
    assert last4 == "1111"
