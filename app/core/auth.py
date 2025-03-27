from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client
from functools import wraps
from app.core.config import settings


class SupabaseAuth:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.security = HTTPBearer()

    async def verify_token(
        self, request: Request, credentials: HTTPAuthorizationCredentials
    ):
        """
        Verify the JWT token from Supabase
        """
        try:
            # Verify the token with Supabase
            user = self.supabase.auth.get_user(credentials.credentials)
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        """
        Dependency to get the current authenticated user
        """
        try:
            # Verify the token with Supabase
            user = self.supabase.auth.get_user(credentials.credentials)
            return user.user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Keep the decorator for backward compatibility
    def require_auth(self, func):
        """
        Decorator to require authentication for routes (legacy support)
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise HTTPException(status_code=500, detail="Request not found")

            # Get the authorization header
            credentials = await self.security(request)

            # Verify the token
            user = await self.verify_token(request, credentials)

            # Add user to request state
            request.state.user = user

            return await func(*args, **kwargs)

        return wrapper


supabase_auth = SupabaseAuth()
