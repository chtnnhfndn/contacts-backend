from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.auth import supabase_auth
from app.core.error_handling import ContactsException
from app.core.crud import SupabaseCRUD
from app.models.models import ProfileType

router = APIRouter()


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PhoneVerification(BaseModel):
    phone: str


class PhoneVerificationCode(BaseModel):
    phone: str
    code: str


@router.post("/register", status_code=201)
async def register_user(user_data: UserRegistration):
    """
    User registration endpoint using Supabase Auth
    """
    try:
        # Validate input data
        if not user_data.password or len(user_data.password) < 8:
            raise ContactsException(
                error_code="INVALID_PASSWORD",
                message="Password must be at least 8 characters long",
            )

        # Use Supabase Auth for user registration
        auth_data = {
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {"full_name": user_data.full_name, "phone": user_data.phone}
            },
        }

        # Register the user with Supabase Auth
        response = supabase_auth.supabase.auth.sign_up(auth_data)

        return {
            "user_id": response.user.id,
            "email": response.user.email,
            "phone": response.user.phone,
            "user_metadata": response.user.user_metadata,
        }
    except Exception as e:
        # Use custom error handling
        raise ContactsException(error_code="REGISTRATION_FAILED", message=str(e))


@router.post("/login")
async def login_user(user_data: UserLogin):
    """
    User login endpoint
    """
    try:
        # Use Supabase for authentication
        response = supabase_auth.supabase.auth.sign_in_with_password(
            {"email": user_data.email, "password": user_data.password}
        )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id,
        }
    except Exception as e:
        raise ContactsException(
            error_code="LOGIN_FAILED",
            message=str(e) or "Login failed. Please check your credentials.",
        )


@router.post("/phone/send-verification")
async def send_phone_verification(
    data: PhoneVerification, current_user=Depends(supabase_auth.get_current_user)
):
    """
    Send a verification code to a user's phone
    """
    try:
        # Use Supabase to send the phone verification code
        supabase_auth.supabase.auth.sign_in_with_otp({"phone": data.phone})

        return {"message": "Verification code sent to your phone"}
    except Exception as e:
        raise ContactsException(error_code="PHONE_VERIFICATION_FAILED", message=str(e))


@router.post("/phone/verify")
async def verify_phone(
    data: PhoneVerificationCode, current_user=Depends(supabase_auth.get_current_user)
):
    """
    Verify a phone with the code sent
    """
    try:
        # Verify the phone with the provided code
        supabase_auth.supabase.auth.verify_otp(
            {"phone": data.phone, "token": data.code, "type": "sms"}
        )

        # Update user metadata
        supabase_auth.supabase.auth.update_user(
            {"phone": data.phone, "phone_confirmed_at": "now()"}
        )

        return {"message": "Phone verified successfully"}
    except Exception as e:
        raise ContactsException(error_code="VERIFICATION_FAILED", message=str(e))


@router.get("/profile")
async def get_user_profile(current_user=Depends(supabase_auth.get_current_user)):
    """
    Get user profile with authentication
    """
    try:
        # The user data is already available from the current_user dependency
        return {
            "id": current_user.id,
            "email": current_user.email,
            "phone": current_user.phone,
            "user_metadata": current_user.user_metadata,
        }
    except Exception:
        raise ContactsException(
            error_code="PROFILE_RETRIEVAL_FAILED",
            message="Could not retrieve user profile",
        )


@router.put("/profile")
async def update_user_profile(
    update_data: Dict[str, Any], current_user=Depends(supabase_auth.get_current_user)
):
    """
    Update user profile
    """
    try:
        # Update the user metadata
        response = supabase_auth.supabase.auth.update_user(
            {"user_metadata": update_data}
        )

        return {
            "id": response.user.id,
            "email": response.user.email,
            "phone": response.user.phone,
            "user_metadata": response.user.user_metadata,
        }
    except Exception as e:
        raise ContactsException(error_code="PROFILE_UPDATE_FAILED", message=str(e))


@router.delete("/profile")
async def delete_user_account(current_user=Depends(supabase_auth.get_current_user)):
    """
    Delete the user's account and all associated data
    """
    user_id = current_user.id

    try:
        # Get all profiles for the user
        profile_crud = SupabaseCRUD("profiles")
        profiles = await profile_crud.read({"user_id": user_id})

        # Helper function to delete type-specific profile data
        async def delete_profile_by_type(profile_type: str, profile_id: UUID) -> None:
            if profile_type == ProfileType.FAMILY.value:
                family_profile_crud = SupabaseCRUD("family_profiles")
                await family_profile_crud.delete("profile_id", profile_id)
            elif profile_type == ProfileType.FRIENDS.value:
                friends_profile_crud = SupabaseCRUD("friends_profiles")
                await friends_profile_crud.delete("profile_id", profile_id)
            elif profile_type == ProfileType.WORK.value:
                work_profile_crud = SupabaseCRUD("work_profiles")
                await work_profile_crud.delete("profile_id", profile_id)
            elif profile_type == ProfileType.ACQUAINTANCES.value:
                acquaintances_profile_crud = SupabaseCRUD("acquaintances_profiles")
                await acquaintances_profile_crud.delete("profile_id", profile_id)

        # Delete all profiles
        for profile in profiles:
            profile_id = profile["id"]
            profile_type = profile["type"]

            # Delete the type-specific profile
            await delete_profile_by_type(profile_type, profile_id)

            # Delete the base profile
            await profile_crud.delete("id", profile_id)

        # Delete all connections
        connections_crud = SupabaseCRUD("connections")

        # Delete connections where user is the owner
        await connections_crud.delete_many("user_id", user_id)

        # Delete connections where user is the connected user
        await connections_crud.delete_many("connected_user_id", user_id)

        # Delete all NFC tokens
        nfc_crud = SupabaseCRUD("nfc_tokens")
        await nfc_crud.delete_many("user_id", user_id)

        # Delete the Supabase user
        supabase_auth.supabase.auth.admin.delete_user(user_id)

        return {"message": "User account and all associated data deleted successfully"}
    except Exception as e:
        raise ContactsException(
            error_code="ACCOUNT_DELETION_FAILED",
            message=f"Failed to delete account: {str(e)}",
        )
