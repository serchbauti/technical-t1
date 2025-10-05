from __future__ import annotations

import random
from typing import Iterable, List, Tuple


def _luhn_sum(digits: Iterable[int]) -> int:
    """
    Compute the Luhn sum over the full sequence (including check digit if present).
    Starting from the rightmost digit, double every second digit; if result > 9, subtract 9.
    """
    s = 0
    for i, d in enumerate(reversed(list(digits))):
        if i % 2 == 0:
            s += d
        else:
            x = d * 2
            s += x - 9 if x > 9 else x
    return s


def is_valid_luhn(number: str) -> bool:
    """
    Validate a numeric string with the Luhn algorithm.
    Returns True if the whole number (including its last check digit) is valid.
    """
    if not number or not number.isdigit():
        return False
    return _luhn_sum(int(c) for c in number) % 10 == 0


def generate_luhn(bin_prefix: str, length: int = 16) -> str:
    """
    Generate a valid PAN-like number with the given BIN prefix and total length.
    The last digit is the Luhn check digit.
    """
    if not bin_prefix.isdigit():
        raise ValueError("BIN must be numeric")
    if len(bin_prefix) >= length:
        raise ValueError("BIN length must be smaller than final length")

    body_len = length - len(bin_prefix) - 1
    body = [random.randint(0, 9) for _ in range(body_len)]
    partial = [int(c) for c in bin_prefix] + body

    # Compute the check digit such that total % 10 == 0
    check_digit = (10 - (_luhn_sum(partial + [0]) % 10)) % 10
    return "".join(map(str, partial + [check_digit]))


def mask_pan(pan: str, mask_char: str = "*") -> str:
    """
    Return a masked representation of a PAN-like string, preserving only the last 4 digits.
    Keeps original length and replaces the rest with mask_char.
    """
    if not pan or len(pan) < 4:
        raise ValueError("PAN must be at least 4 characters long")
    last4 = pan[-4:]
    return f"{mask_char * (len(pan) - 4)}{last4}"


def derive_bin_last4(pan: str) -> Tuple[str, str]:
    """
    Convenience helper to derive BIN (first 6) and last4 from a PAN-like string.
    """
    if not pan or not pan.isdigit() or len(pan) < 10:
        raise ValueError("PAN must be numeric and at least 10 digits long")
    return pan[:6], pan[-4:]
