import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from supabase import Client
from supabase import AuthApiError

from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import UserCreate, UserInDB


class AuthService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def register_user(self, user: UserCreate) -> UserInDB:
        """
        Register a new user in Supabase

        Args:
            user (UserCreate): User registration details

        Returns:
            UserInDB: Registered user details
        """
        try:
            # Sign up with Supabase Auth
            supabase_user = self.supabase.auth.sign_up(
                {"email": user.email, "password": user.password}
            )

            # Prepare user data for database insertion
            new_user_data = {
                "id": supabase_user.user.id,
                "email": user.email,
                "hashed_password": get_password_hash(user.password),
                "is_active": True,
                "is_verified": False,
                "phone_number": user.phone_number,
            }

            # Insert user in Supabase Users table
            self.supabase.table("users").insert(new_user_data).execute()

            return UserInDB(**new_user_data)

        except AuthApiError as e:
            raise ValueError(f"Registration failed: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with Supabase

        Args:
            email (str): User's email
            password (str): User's password

        Returns:
            Optional[UserInDB]: Authenticated user details
        """
        try:
            # Authenticate with Supabase
            self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            # Retrieve user details from Users table
            user_result = (
                self.supabase.table("users").select("*").eq("email", email).execute()
            )

            if not user_result.data:
                raise ValueError("User not found")

            user_data = user_result.data[0]

            # Extra verification (optional)
            if not verify_password(password, user_data.get("hashed_password", "")):
                raise ValueError("Invalid credentials")

            return UserInDB(**user_data)

        except AuthApiError as e:
            raise ValueError(f"Authentication failed: {str(e)}")

    async def create_user_token(self, user: UserInDB) -> Dict[str, str]:
        """
        Create access token for authenticated user

        Args:
            user (UserInDB): Authenticated user

        Returns:
            Dict[str, str]: Token details
        """
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}


class ProfileService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def update_profile(
        self, user_id: str, profile_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile in Supabase

        Args:
            user_id (str): Supabase user ID
            profile_update (Dict[str, Any]): Profile update details

        Returns:
            Dict[str, Any]: Updated profile
        """
        # Validate profile type
        valid_profile_types = ["personal", "professional", "social"]

        if (
            profile_update.get("profile_type")
            and profile_update["profile_type"] not in valid_profile_types
        ):
            raise ValueError(
                f"Invalid profile type. Must be one of {valid_profile_types}"
            )

        # Update user metadata in Supabase
        try:
            # Update user metadata
            self.supabase.auth.update_user({"data": profile_update})

            # Update user details in users table
            result = (
                self.supabase.table("users")
                .update(profile_update)
                .eq("id", user_id)
                .execute()
            )

            return result.data[0] if result.data else {}

        except Exception as e:
            raise ValueError(f"Profile update failed: {str(e)}")

    async def get_specific_profile(
        self, user_id: str, profile_type: str
    ) -> Dict[str, Any]:
        """
        Retrieve a specific profile for the user

        Args:
            user_id (str): Supabase user ID
            profile_type (str): Type of profile to retrieve

        Returns:
            Dict[str, Any]: Profile details
        """
        valid_profile_types = ["personal", "professional", "social"]

        if profile_type not in valid_profile_types:
            raise ValueError(
                f"Invalid profile type. Must be one of {valid_profile_types}"
            )

        try:
            # Retrieve user profile from Supabase
            result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )

            return result.data or {}

        except Exception as e:
            raise ValueError(f"Profile retrieval failed: {str(e)}")


class NFCSharingService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def generate_nfc_token(
        self, user_id: str, profile_type: str
    ) -> Dict[str, Any]:
        """
        Generate an NFC sharing token

        Args:
            user_id (str): Supabase user ID
            profile_type (str): Profile type for NFC sharing

        Returns:
            Dict[str, Any]: NFC token details
        """
        valid_profile_types = ["personal", "professional", "social"]

        if profile_type not in valid_profile_types:
            raise ValueError(
                f"Invalid profile type. Must be one of {valid_profile_types}"
            )

        # Create unique token
        token = str(uuid.uuid4())

        # Set expiration (default 24 hours)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Create NFC token in Supabase
        try:
            nfc_token_data = {
                "user_id": user_id,
                "token": token,
                "profile_type": profile_type,
                "expires_at": expires_at.isoformat(),
                "is_active": True,
            }

            result = self.supabase.table("nfc_tokens").insert(nfc_token_data).execute()

            return result.data[0] if result.data else {}

        except Exception as e:
            raise ValueError(f"NFC token generation failed: {str(e)}")

    async def share_profile_via_nfc(
        self, current_user_id: str, nfc_token: str
    ) -> Dict[str, Any]:
        """
        Share a profile via NFC token

        Args:
            current_user_id (str): Current user's ID
            nfc_token (str): NFC token for profile sharing

        Returns:
            Dict[str, Any]: Shared profile details
        """
        try:
            # Find the NFC token
            token_result = (
                self.supabase.table("nfc_tokens")
                .select("*")
                .eq("token", nfc_token)
                .single()
                .execute()
            )

            token_data = token_result.data

            # Validate token
            if not token_data:
                raise ValueError("Invalid NFC token")

            # Check token expiration
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if expires_at < datetime.utcnow():
                raise ValueError("NFC token has expired")

            # Ensure the token belongs to a different user
            if token_data["user_id"] == current_user_id:
                raise ValueError("Cannot use your own NFC token")

            # Retrieve token owner's profile
            user_result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", token_data["user_id"])
                .single()
                .execute()
            )

            return user_result.data or {}

        except Exception as e:
            raise ValueError(f"NFC profile sharing failed: {str(e)}")

    async def get_user_nfc_tokens(self, user_id: str) -> list:
        """
        Retrieve all active NFC tokens for the current user

        Args:
            user_id (str): Supabase user ID

        Returns:
            list: Active NFC tokens
        """
        try:
            # Query active NFC tokens
            result = (
                self.supabase.table("nfc_tokens")
                .select("*")
                .eq("user_id", user_id)
                .gt("expires_at", datetime.utcnow().isoformat())
                .execute()
            )

            return result.data or []

        except Exception as e:
            raise ValueError(f"NFC tokens retrieval failed: {str(e)}")
