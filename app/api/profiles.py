from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import date

from app.core.auth import supabase_auth
from app.core.error_handling import ContactsException
from app.core.crud import SupabaseCRUD
from app.models.models import ProfileType


router = APIRouter()
profile_crud = SupabaseCRUD("profiles")
family_profile_crud = SupabaseCRUD("family_profiles")
friends_profile_crud = SupabaseCRUD("friends_profiles")
work_profile_crud = SupabaseCRUD("work_profiles")
acquaintances_profile_crud = SupabaseCRUD("acquaintances_profiles")


# Input models for creating profiles
class FamilyProfileCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    whatsapp: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class FriendsProfileCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    instagram: Optional[str] = None
    snapchat: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class WorkProfileCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    linkedin: Optional[str] = None
    resume: Optional[str] = None
    website: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class AcquaintanceProfileCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {"str_strip_whitespace": True}


@router.post("/family", status_code=201)
async def create_family_profile(
    profile_data: FamilyProfileCreate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Create a new family profile for the authenticated user
    """
    user_id = current_user.id

    try:
        # Check if user already has a family profile
        existing_profiles = await profile_crud.read(
            {"user_id": user_id, "type": ProfileType.FAMILY.value}
        )

        if existing_profiles:
            raise ContactsException(
                error_code="PROFILE_EXISTS", message="Family profile already exists"
            )

        # Create base profile
        base_profile = await profile_crud.create(
            {
                "user_id": user_id,
                "name": profile_data.name,
                "type": ProfileType.FAMILY.value,
                "photo": profile_data.photo,
            }
        )

        # Create family profile
        family_profile = await family_profile_crud.create(
            {
                "profile_id": base_profile["id"],
                "phone_number": profile_data.phone_number,
                "email": profile_data.email,
                "date_of_birth": (
                    profile_data.date_of_birth.isoformat()
                    if profile_data.date_of_birth
                    else None
                ),
                "whatsapp": profile_data.whatsapp,
            }
        )

        # Combine the results
        result = {**base_profile, **family_profile}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_CREATION_FAILED", message=str(e))


@router.post("/friends", status_code=201)
async def create_friends_profile(
    profile_data: FriendsProfileCreate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Create a new friends profile for the authenticated user
    """
    user_id = current_user.id

    try:
        # Check if user already has a friends profile
        existing_profiles = await profile_crud.read(
            {"user_id": user_id, "type": ProfileType.FRIENDS.value}
        )

        if existing_profiles:
            raise ContactsException(
                error_code="PROFILE_EXISTS", message="Friends profile already exists"
            )

        # Create base profile
        base_profile = await profile_crud.create(
            {
                "user_id": user_id,
                "name": profile_data.name,
                "type": ProfileType.FRIENDS.value,
                "photo": profile_data.photo,
            }
        )

        # Create friends profile
        friends_profile = await friends_profile_crud.create(
            {
                "profile_id": base_profile["id"],
                "phone_number": profile_data.phone_number,
                "email": profile_data.email,
                "instagram": profile_data.instagram,
                "snapchat": profile_data.snapchat,
            }
        )

        # Combine the results
        result = {**base_profile, **friends_profile}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_CREATION_FAILED", message=str(e))


@router.post("/work", status_code=201)
async def create_work_profile(
    profile_data: WorkProfileCreate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Create a new work profile for the authenticated user
    """
    user_id = current_user.id

    try:
        # Check if user already has a work profile
        existing_profiles = await profile_crud.read(
            {"user_id": user_id, "type": ProfileType.WORK.value}
        )

        if existing_profiles:
            raise ContactsException(
                error_code="PROFILE_EXISTS", message="Work profile already exists"
            )

        # Create base profile
        base_profile = await profile_crud.create(
            {
                "user_id": user_id,
                "name": profile_data.name,
                "type": ProfileType.WORK.value,
                "photo": profile_data.photo,
            }
        )

        # Create work profile
        work_profile = await work_profile_crud.create(
            {
                "profile_id": base_profile["id"],
                "whatsapp": profile_data.whatsapp,
                "telegram": profile_data.telegram,
                "linkedin": profile_data.linkedin,
                "resume": profile_data.resume,
                "website": profile_data.website,
            }
        )

        # Combine the results
        result = {**base_profile, **work_profile}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_CREATION_FAILED", message=str(e))


@router.post("/acquaintance", status_code=201)
async def create_acquaintance_profile(
    profile_data: AcquaintanceProfileCreate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Create a new acquaintance profile for the authenticated user
    """
    user_id = current_user.id

    try:
        # Check if user already has an acquaintance profile
        existing_profiles = await profile_crud.read(
            {"user_id": user_id, "type": ProfileType.ACQUAINTANCES.value}
        )

        if existing_profiles:
            raise ContactsException(
                error_code="PROFILE_EXISTS",
                message="Acquaintance profile already exists",
            )

        # Create base profile
        base_profile = await profile_crud.create(
            {
                "user_id": user_id,
                "name": profile_data.name,
                "type": ProfileType.ACQUAINTANCES.value,
                "photo": profile_data.photo,
            }
        )

        # Create acquaintance profile
        acquaintance_profile = await acquaintances_profile_crud.create(
            {"profile_id": base_profile["id"], "email": profile_data.email}
        )

        # Combine the results
        result = {**base_profile, **acquaintance_profile}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_CREATION_FAILED", message=str(e))


# Add these helper functions before the list_profiles endpoint
async def get_type_specific_details(profile_type: str, profile_id: UUID) -> dict:
    """Get the type-specific details for a profile"""
    if profile_type == ProfileType.FAMILY.value:
        return await family_profile_crud.get_by_id("profile_id", profile_id) or {}
    elif profile_type == ProfileType.FRIENDS.value:
        return await friends_profile_crud.get_by_id("profile_id", profile_id) or {}
    elif profile_type == ProfileType.WORK.value:
        return await work_profile_crud.get_by_id("profile_id", profile_id) or {}
    elif profile_type == ProfileType.ACQUAINTANCES.value:
        return (
            await acquaintances_profile_crud.get_by_id("profile_id", profile_id) or {}
        )
    return {}


async def get_enriched_profile(profile: dict, user_id: str) -> dict:
    """Enrich a profile with its type-specific details"""
    profile_id = profile["id"]
    profile_type = profile["type"]

    details = await get_type_specific_details(profile_type, profile_id)
    return {**profile, **details, "is_own": profile["user_id"] == user_id}


async def get_user_profiles(user_id: str) -> list:
    """Get detailed profiles for a user"""
    # Get all profiles for the user
    profiles = await profile_crud.read({"user_id": user_id})

    # Add details to each profile
    return [await get_enriched_profile(profile, user_id) for profile in profiles]


async def get_connection_profiles(user_id: str) -> list:
    """Get profiles of users connected to the given user"""
    connections_crud = SupabaseCRUD("connections")

    # Get all user's connections
    connections = await connections_crud.read({"user_id": user_id})

    result = []
    # Get profiles for each connected user
    for connection in connections:
        connected_user_id = connection["connected_user_id"]
        connection_type = connection["connection_type"]

        # Get profiles of the connected user
        connected_profiles = await profile_crud.read({"user_id": connected_user_id})

        # Add each profile with connection information
        for profile in connected_profiles:
            detailed_profile = await get_enriched_profile(profile, user_id)
            detailed_profile["connection_id"] = connection["id"]
            detailed_profile["connection_type"] = connection_type
            detailed_profile["is_own"] = False
            result.append(detailed_profile)

    return result


@router.get("/")
async def list_profiles(
    include_connections: bool = True,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    List all profiles for the authenticated user and optionally their connections
    """
    user_id = current_user.id

    try:
        # Get user's own profiles
        detailed_profiles = await get_user_profiles(user_id)

        # If including connections, add connected users' profiles
        if include_connections:
            connection_profiles = await get_connection_profiles(user_id)
            detailed_profiles.extend(connection_profiles)

        return detailed_profiles
    except Exception as e:
        raise ContactsException(
            error_code="PROFILE_RETRIEVAL_FAILED",
            message=f"Failed to retrieve profiles: {str(e)}",
        )


@router.get("/{profile_id}")
async def get_profile(
    profile_id: UUID, current_user=Depends(supabase_auth.get_current_user)
):
    """
    Get a specific profile by ID
    """
    user_id = current_user.id

    try:
        # Get the base profile
        profile = await profile_crud.get_by_id("id", profile_id)

        if not profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        # Verify that the profile belongs to the user
        if profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to access this profile",
            )

        # Get the detailed profile based on type
        profile_type = profile["type"]

        if profile_type == ProfileType.FAMILY.value:
            details = await family_profile_crud.get_by_id("profile_id", profile_id)
        elif profile_type == ProfileType.FRIENDS.value:
            details = await friends_profile_crud.get_by_id("profile_id", profile_id)
        elif profile_type == ProfileType.WORK.value:
            details = await work_profile_crud.get_by_id("profile_id", profile_id)
        elif profile_type == ProfileType.ACQUAINTANCES.value:
            details = await acquaintances_profile_crud.get_by_id(
                "profile_id", profile_id
            )
        else:
            details = {}

        # Combine the results
        result = {**profile, **details}

        return result
    except ContactsException:
        raise
    except Exception:
        raise ContactsException(
            error_code="PROFILE_RETRIEVAL_FAILED", message="Failed to retrieve profile"
        )


# Add this helper function before the delete_profile endpoint
async def delete_profile_by_type(profile_type: str, profile_id: UUID) -> None:
    """Helper function to delete type-specific profile data"""
    if profile_type == ProfileType.FAMILY.value:
        await family_profile_crud.delete("profile_id", profile_id)
    elif profile_type == ProfileType.FRIENDS.value:
        await friends_profile_crud.delete("profile_id", profile_id)
    elif profile_type == ProfileType.WORK.value:
        await work_profile_crud.delete("profile_id", profile_id)
    elif profile_type == ProfileType.ACQUAINTANCES.value:
        await acquaintances_profile_crud.delete("profile_id", profile_id)


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID, current_user=Depends(supabase_auth.get_current_user)
):
    """
    Delete a profile by ID
    """
    user_id = current_user.id

    try:
        # Verify the profile exists and belongs to the user
        existing_profile = await profile_crud.get_by_id("id", profile_id)

        if not existing_profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        if existing_profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to delete this profile",
            )

        # Delete the type-specific profile
        await delete_profile_by_type(existing_profile["type"], profile_id)

        # Delete base profile
        deleted = await profile_crud.delete("id", profile_id)

        if not deleted:
            raise ContactsException(
                error_code="PROFILE_DELETE_FAILED", message="Failed to delete profile"
            )

        return {"message": "Profile deleted successfully"}

    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_DELETE_FAILED", message=str(e))


# PUT routes for updating profiles
class FamilyProfileUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    whatsapp: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class FriendsProfileUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    instagram: Optional[str] = None
    snapchat: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class WorkProfileUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    linkedin: Optional[str] = None
    resume: Optional[str] = None
    website: Optional[str] = None

    model_config = {"str_strip_whitespace": True}


class AcquaintanceProfileUpdate(BaseModel):
    name: Optional[str] = None
    photo: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {"str_strip_whitespace": True}


async def update_base_profile(profile_id: UUID, update_data: dict):
    """Helper function to update base profile data"""
    base_update = {k: v for k, v in update_data.items() if k in ["name", "photo"]}
    if base_update:
        return await profile_crud.update("id", profile_id, base_update)
    return None


@router.put("/family/{profile_id}")
async def update_family_profile(
    profile_id: UUID,
    profile_data: FamilyProfileUpdate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Update an existing family profile
    """
    user_id = current_user.id

    try:
        # Verify the profile exists and belongs to the user
        existing_profile = await profile_crud.get_by_id("id", profile_id)

        if not existing_profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        if existing_profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to modify this profile",
            )

        # Verify it's the correct type
        if existing_profile["type"] != ProfileType.FAMILY.value:
            raise ContactsException(
                error_code="PROFILE_TYPE_MISMATCH",
                message="This is not a family profile",
            )

        # Update base profile (name, photo)
        await update_base_profile(profile_id, profile_data.model_dump())

        # Update family-specific fields
        family_update = {
            k: v
            for k, v in profile_data.model_dump().items()
            if k in ["phone_number", "email", "date_of_birth", "whatsapp"]
            and v is not None
        }

        # Convert date to ISO format if present
        if "date_of_birth" in family_update and family_update["date_of_birth"]:
            family_update["date_of_birth"] = family_update["date_of_birth"].isoformat()

        # Update family profile
        if family_update:
            await family_profile_crud.update("profile_id", profile_id, family_update)

        # Get the updated profile
        updated_profile = await profile_crud.get_by_id("id", profile_id)
        updated_details = await family_profile_crud.get_by_id("profile_id", profile_id)

        # Combine the results
        result = {**updated_profile, **updated_details}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_UPDATE_FAILED", message=str(e))


@router.put("/friends/{profile_id}")
async def update_friends_profile(
    profile_id: UUID,
    profile_data: FriendsProfileUpdate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Update an existing friends profile
    """
    user_id = current_user.id

    try:
        # Verify the profile exists and belongs to the user
        existing_profile = await profile_crud.get_by_id("id", profile_id)

        if not existing_profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        if existing_profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to modify this profile",
            )

        # Verify it's the correct type
        if existing_profile["type"] != ProfileType.FRIENDS.value:
            raise ContactsException(
                error_code="PROFILE_TYPE_MISMATCH",
                message="This is not a friends profile",
            )

        # Update base profile (name, photo)
        await update_base_profile(profile_id, profile_data.model_dump())

        # Update friends-specific fields
        friends_update = {
            k: v
            for k, v in profile_data.model_dump().items()
            if k in ["phone_number", "email", "instagram", "snapchat"] and v is not None
        }

        # Update friends profile
        if friends_update:
            await friends_profile_crud.update("profile_id", profile_id, friends_update)

        # Get the updated profile
        updated_profile = await profile_crud.get_by_id("id", profile_id)
        updated_details = await friends_profile_crud.get_by_id("profile_id", profile_id)

        # Combine the results
        result = {**updated_profile, **updated_details}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_UPDATE_FAILED", message=str(e))


@router.put("/work/{profile_id}")
async def update_work_profile(
    profile_id: UUID,
    profile_data: WorkProfileUpdate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Update an existing work profile
    """
    user_id = current_user.id

    try:
        # Verify the profile exists and belongs to the user
        existing_profile = await profile_crud.get_by_id("id", profile_id)

        if not existing_profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        if existing_profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to modify this profile",
            )

        # Verify it's the correct type
        if existing_profile["type"] != ProfileType.WORK.value:
            raise ContactsException(
                error_code="PROFILE_TYPE_MISMATCH",
                message="This is not a work profile",
            )

        # Update base profile (name, photo)
        await update_base_profile(profile_id, profile_data.model_dump())

        # Update work-specific fields
        work_update = {
            k: v
            for k, v in profile_data.model_dump().items()
            if k in ["whatsapp", "telegram", "linkedin", "resume", "website"]
            and v is not None
        }

        # Update work profile
        if work_update:
            await work_profile_crud.update("profile_id", profile_id, work_update)

        # Get the updated profile
        updated_profile = await profile_crud.get_by_id("id", profile_id)
        updated_details = await work_profile_crud.get_by_id("profile_id", profile_id)

        # Combine the results
        result = {**updated_profile, **updated_details}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_UPDATE_FAILED", message=str(e))


@router.put("/acquaintance/{profile_id}")
async def update_acquaintance_profile(
    profile_id: UUID,
    profile_data: AcquaintanceProfileUpdate,
    current_user=Depends(supabase_auth.get_current_user),
):
    """
    Update an existing acquaintance profile
    """
    user_id = current_user.id

    try:
        # Verify the profile exists and belongs to the user
        existing_profile = await profile_crud.get_by_id("id", profile_id)

        if not existing_profile:
            raise ContactsException(
                error_code="PROFILE_NOT_FOUND", message="Profile not found"
            )

        if existing_profile["user_id"] != user_id:
            raise ContactsException(
                error_code="UNAUTHORIZED",
                message="Not authorized to modify this profile",
            )

        # Verify it's the correct type
        if existing_profile["type"] != ProfileType.ACQUAINTANCES.value:
            raise ContactsException(
                error_code="PROFILE_TYPE_MISMATCH",
                message="This is not an acquaintance profile",
            )

        # Update base profile (name, photo)
        await update_base_profile(profile_id, profile_data.model_dump())

        # Update acquaintance-specific fields
        acquaintance_update = {
            k: v
            for k, v in profile_data.model_dump().items()
            if k in ["email"] and v is not None
        }

        # Update acquaintance profile
        if acquaintance_update:
            await acquaintances_profile_crud.update(
                "profile_id", profile_id, acquaintance_update
            )

        # Get the updated profile
        updated_profile = await profile_crud.get_by_id("id", profile_id)
        updated_details = await acquaintances_profile_crud.get_by_id(
            "profile_id", profile_id
        )

        # Combine the results
        result = {**updated_profile, **updated_details}

        return result
    except ContactsException:
        raise
    except Exception as e:
        raise ContactsException(error_code="PROFILE_UPDATE_FAILED", message=str(e))
