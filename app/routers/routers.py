from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client

from app.core.database import get_supabase_client
from app.core.security import get_current_user
from app.models.models import UserCreate, UserInDB, UserResponse
from app.services.services import AuthService, ProfileService, NFCSharingService

# Auth Router
auth_router = APIRouter()


@auth_router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate, supabase_client: Client = Depends(get_supabase_client)
):
    """Register a new user"""
    try:
        auth_service = AuthService(supabase_client)
        registered_user = await auth_service.register_user(user)
        return UserResponse(**registered_user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase_client: Client = Depends(get_supabase_client),
):
    """OAuth2 compatible token login"""
    try:
        auth_service = AuthService(supabase_client)
        user = await auth_service.authenticate_user(
            form_data.username, form_data.password
        )
        return await auth_service.create_user_token(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Profile Router
profile_router = APIRouter()


@profile_router.patch("/update")
async def update_profile(
    profile_update: dict,  # Flexible profile update
    current_user: UserInDB = Depends(get_current_user),
    supabase_client: Client = Depends(get_supabase_client),
):
    """Update profile for the current user"""
    try:
        profile_service = ProfileService(supabase_client)
        updated_profile = await profile_service.update_profile(
            current_user.id, profile_update
        )
        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@profile_router.get("/me")
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Retrieve the current user's profile"""
    return current_user


@profile_router.get("/{profile_type}")
async def get_specific_profile(
    profile_type: str,
    current_user: UserInDB = Depends(get_current_user),
    supabase_client: Client = Depends(get_supabase_client),
):
    """Retrieve a specific profile for the current user"""
    try:
        profile_service = ProfileService(supabase_client)
        profile = await profile_service.get_specific_profile(
            current_user.id, profile_type
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# NFC Sharing Router
nfc_router = APIRouter()


@nfc_router.post("/generate-token")
async def generate_nfc_token(
    profile_type: str,
    current_user: UserInDB = Depends(get_current_user),
    supabase_client: Client = Depends(get_supabase_client),
):
    """Generate an NFC sharing token for a specific profile"""
    try:
        nfc_service = NFCSharingService(supabase_client)
        nfc_token = await nfc_service.generate_nfc_token(current_user.id, profile_type)
        return nfc_token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@nfc_router.post("/share")
async def share_profile_via_nfc(
    nfc_token: str,
    current_user: UserInDB = Depends(get_current_user),
    supabase_client: Client = Depends(get_supabase_client),
):
    """Share a profile via NFC token"""
    try:
        nfc_service = NFCSharingService(supabase_client)
        shared_profile = await nfc_service.share_profile_via_nfc(
            current_user.id, nfc_token
        )
        return shared_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@nfc_router.get("/tokens")
async def get_user_nfc_tokens(
    current_user: UserInDB = Depends(get_current_user),
    supabase_client: Client = Depends(get_supabase_client),
):
    """Retrieve all NFC tokens for the current user"""
    nfc_service = NFCSharingService(supabase_client)
    tokens = await nfc_service.get_user_nfc_tokens(current_user.id)
    return tokens
