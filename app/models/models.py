from pydantic import BaseModel, EmailStr, ConfigDict, HttpUrl
from datetime import datetime, date
from typing import Optional, Literal, Union
from enum import Enum


class ConnectionType(str, Enum):
    """Enum for different types of connections"""

    FAMILY = "family"
    FRIEND = "friend"
    WORK = "work"
    ACQUAINTANCE = "acquaintance"


class ProfileType(str, Enum):
    """Enum for different types of profiles"""

    FAMILY = "family"
    FRIENDS = "friends"
    WORK = "work"
    ACQUAINTANCES = "acquaintances"


class UserBase(BaseModel):
    """Base User model for input/output validation"""

    email: EmailStr
    phone_number: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None


class UserCreate(UserBase):
    """User model for user creation"""

    password: str


class UserInDB(UserBase):
    """User model for database storage"""

    id: str  # UUID from Supabase
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Common profile fields
class ProfileBase(BaseModel):
    """Base Profile model with common fields"""

    name: str
    type: ProfileType
    photo: Optional[str] = None


# Family profile fields
class FamilyProfile(ProfileBase):
    """Family profile model"""

    type: Literal[ProfileType.FAMILY]
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    whatsapp: Optional[str] = None


# Friends profile fields
class FriendsProfile(ProfileBase):
    """Friends profile model"""

    type: Literal[ProfileType.FRIENDS]
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    instagram: Optional[str] = None
    snapchat: Optional[str] = None


# Work profile fields
class WorkProfile(ProfileBase):
    """Work profile model"""

    type: Literal[ProfileType.WORK]
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    linkedin: Optional[str] = None
    resume: Optional[str] = None
    website: Optional[HttpUrl] = None


# Acquaintance profile fields
class AcquaintanceProfile(ProfileBase):
    """Acquaintance profile model"""

    type: Literal[ProfileType.ACQUAINTANCES]
    email: Optional[EmailStr] = None


# Union of all profile types
Profile = Union[FamilyProfile, FriendsProfile, WorkProfile, AcquaintanceProfile]


class ProfileCreate(BaseModel):
    """Profile model for creation"""

    user_id: str
    profile_data: Profile


class ProfileInDB(BaseModel):
    """Profile model for database storage"""

    id: str
    user_id: str
    data: Profile
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectionBase(BaseModel):
    """Base Connection model"""

    user_id: str
    connected_user_id: str
    connection_type: ConnectionType


class ConnectionInDB(ConnectionBase):
    """Connection model for database storage"""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NFCTokenBase(BaseModel):
    """Base NFC Token model"""

    user_id: str
    token: str
    profile_type: ProfileType
    is_active: bool = True
    expires_at: Optional[datetime] = None


class NFCTokenInDB(NFCTokenBase):
    """NFC Token model for database storage"""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
