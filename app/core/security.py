from datetime import datetime, timedelta
from typing import Optional, NamedTuple
import secrets

from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class NFCTokenDetails(NamedTuple):
    """Structured representation of NFC token details."""

    token: str
    expires_at: datetime


def get_password_hash(password: str) -> str:
    """
    Generate a secure hash for the given password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with optional expiration.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def generate_nfc_token(
    user_id: int, profile_id: int, expiry: Optional[int] = None
) -> NFCTokenDetails:
    """
    Generate a secure, time-limited NFC sharing token.

    Args:
        user_id: ID of the user generating the token
        profile_id: ID of the profile being shared
        expiry: Optional custom expiry time in seconds

    Returns:
        NFCTokenDetails with token and expiration time
    """
    expiry = expiry or settings.NFC_SHARE_EXPIRY

    # Generate a cryptographically secure token
    token = secrets.token_urlsafe(32)

    # Token expires after specified duration
    expires_at = datetime.utcnow() + timedelta(seconds=expiry)

    return NFCTokenDetails(token=token, expires_at=expires_at)
