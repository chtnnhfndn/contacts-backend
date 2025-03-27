from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timedelta, timezone
import secrets
import string

from app.core.auth import supabase_auth
from app.core.error_handling import ContactsException
from app.core.crud import SupabaseCRUD
from app.core.config import settings


router = APIRouter()
nfc_crud = SupabaseCRUD("nfc_tokens")
profile_crud = SupabaseCRUD("profiles")


class NFCTokenCreate(BaseModel):
    profile_type: Literal["family", "friends", "work", "acquaintances"]


class NFCTokenResponse(BaseModel):
    token: str
    profile_type: str
    expires_at: datetime


def generate_token(length: int = 32) -> str:
    """Generate a secure random token for NFC sharing"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("/generate", response_model=NFCTokenResponse)
async def generate_nfc_token(
    token_data: NFCTokenCreate, current_user=Depends(supabase_auth.get_current_user)
):
    """
    Generate a new NFC token for sharing a specific profile
    """
    user_id = current_user.id

    try:
        # Verify the profile exists
        profiles = await profile_crud.read(
            {"user_id": user_id, "type": token_data.profile_type}
        )

        if not profiles:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND",
                message=f"Profile of type '{token_data.profile_type}' not found",
            )

        # Generate expiration time (use timezone-aware datetime)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.NFC_TOKEN_EXPIRE_MINUTES
        )

        # Generate token
        token = generate_token()

        # Invalidate existing tokens for this profile type
        existing_tokens = await nfc_crud.read(
            {
                "user_id": user_id,
                "profile_type": token_data.profile_type,
                "is_active": True,
            }
        )

        for existing_token in existing_tokens:
            await nfc_crud.update("id", existing_token["id"], {"is_active": False})

        # Create new token
        token_data_dict = {
            "user_id": user_id,
            "token": token,
            "profile_type": token_data.profile_type,
            "is_active": True,
            "expires_at": expires_at.isoformat(),
        }

        await nfc_crud.create(token_data_dict)

        return NFCTokenResponse(
            token=token,
            profile_type=token_data_dict["profile_type"],
            expires_at=expires_at,
        )
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="TOKEN_GENERATION_FAILED", message=str(e))


@router.get("/validate/{token}")
async def validate_nfc_token(token: str = Path(...)):
    """
    Validate an NFC token and return the associated profile if valid
    """
    try:
        # Find token
        tokens = await nfc_crud.read({"token": token, "is_active": True})

        if not tokens:
            raise ContactsException(
                error_code="INVALID_TOKEN", message="Invalid or expired token"
            )

        token_data = tokens[0]

        # Check if token is expired
        expires_at = datetime.fromisoformat(
            token_data["expires_at"].replace("Z", "+00:00")
        )
        # Create a timezone-aware current time
        now = datetime.now(timezone.utc)

        if expires_at < now:
            # Deactivate expired token
            await nfc_crud.update("id", token_data["id"], {"is_active": False})
            raise ContactsException(
                error_code="EXPIRED_TOKEN", message="Token has expired"
            )

        # Get associated profile
        profile = await profile_crud.read(
            {"user_id": token_data["user_id"], "type": token_data["profile_type"]}
        )

        if not profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Associated profile not found"
            )

        # Return profile data
        return {"profile": profile[0], "user_id": token_data["user_id"]}
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="TOKEN_VALIDATION_FAILED", message=str(e))


@router.post("/connect/{token}")
async def connect_via_nfc(
    token: str = Path(...), current_user=Depends(supabase_auth.get_current_user)
):
    """
    Connect with a user using their NFC token
    """
    user_id = current_user.id
    connections_crud = SupabaseCRUD("connections")

    try:
        # Validate token
        tokens = await nfc_crud.read({"token": token, "is_active": True})

        if not tokens:
            raise ContactsException(
                error_code="INVALID_TOKEN", message="Invalid or expired token"
            )

        token_data = tokens[0]
        target_user_id = token_data["user_id"]

        # Prevent self-connection
        if user_id == target_user_id:
            raise ContactsException(
                error_code="SELF_CONNECTION", message="Cannot connect with yourself"
            )

        # Check if token is expired
        expires_at = datetime.fromisoformat(
            token_data["expires_at"].replace("Z", "+00:00")
        )
        # Create a timezone-aware current time
        now = datetime.now(timezone.utc)

        if expires_at < now:
            # Deactivate expired token
            await nfc_crud.update("id", token_data["id"], {"is_active": False})
            raise ContactsException(
                error_code="EXPIRED_TOKEN", message="Token has expired"
            )

        # Check if connection already exists
        existing_connection = await connections_crud.read(
            {"user_id": user_id, "connected_user_id": target_user_id}
        )

        if existing_connection:
            raise ContactsException(
                error_code="CONNECTION_EXISTS", message="Connection already exists"
            )

        # Create connection
        connection_data = {
            "user_id": user_id,
            "connected_user_id": target_user_id,
            "connection_type": token_data["profile_type"],
        }

        new_connection = await connections_crud.create(connection_data)

        # Invalidate token after use
        await nfc_crud.update("id", token_data["id"], {"is_active": False})

        # Get profile data
        profile = await profile_crud.read(
            {"user_id": target_user_id, "type": token_data["profile_type"]}
        )

        return {
            "message": "Connection created successfully",
            "connection": new_connection,
            "profile": profile[0] if profile else None,
        }
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="CONNECTION_FAILED", message=str(e))
