from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema for common user attributes."""

    email: EmailStr
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Response schema for user information."""

    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    """Base profile schema."""

    name: str
    type: str = Field(..., pattern="^(family|friends|work|acquaintances)$")
    visibility_settings: Optional[str] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile."""

    pass


class ProfileResponse(ProfileBase):
    """Response schema for profile information."""

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class NFCTokenCreate(BaseModel):
    """Schema for creating an NFC sharing token."""

    profile_id: int


class NFCTokenResponse(BaseModel):
    """Response schema for NFC token."""

    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfilesResponse(UserResponse):
    """Response schema including user's profiles."""

    profiles: List[ProfileResponse] = []
