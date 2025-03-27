from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NFCTokenCreate(BaseModel):
    """Schema for creating an NFC token"""

    profile_type: str = Field(
        ...,
        description="Type of profile to share",
        pattern="^(family|friends|work|acquaintances)$",
    )
    expires_at: Optional[datetime] = None


class NFCTokenResponse(BaseModel):
    """Schema for returning NFC token details"""

    token: str
    profile_type: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]


class NFCShareRequest(BaseModel):
    """Schema for NFC sharing request"""

    token: str
    target_user_id: Optional[int] = None  # Optional for anonymous sharing
