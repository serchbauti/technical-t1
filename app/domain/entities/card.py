from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

class Card(BaseModel):
    """
    Domain entity for Card (without full PAN).
    """
    id: str | None = None
    client_id: str
    pan_masked: str
    last4: str
    bin: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("last4")
    @classmethod
    def validate_last4(cls, v: str) -> str:
        if len(v) != 4 or not v.isdigit():
            raise ValueError("last4 must be exactly 4 numeric digits")
        return v

    @field_validator("bin")
    @classmethod
    def validate_bin(cls, v: str) -> str:
        if len(v) != 6 or not v.isdigit():
            raise ValueError("bin must be exactly 6 numeric digits")
        return v

    @field_validator("pan_masked")
    @classmethod
    def validate_pan_masked(cls, v: str, info):
        # Simple rules: at least 12 chars, ends with last4 and previous chars must not contain visible digits
        if len(v) < 12:
            raise ValueError("pan_masked must have a minimum length of 12 characters")
        # If last4 is available in validated values, verify consistency
        last4 = info.data.get("last4")
        if last4 and not v.endswith(last4):
            raise ValueError("pan_masked must end with last4")
        # Everything before last4 must be masked (non-numeric): typically '*'
        masked_part = v[:-4] if last4 else v[:-4]
        if any(ch.isdigit() for ch in masked_part):
            raise ValueError("pan_masked must mask digits before last4")
        return v

    def touch(self) -> None:
        """Updates the modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)
