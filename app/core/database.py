from supabase import create_client, Client
from app.core.config import settings
from typing import Optional, AsyncGenerator


class SupabaseManager:
    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Create or return an existing Supabase client.

        Returns:
            Supabase Client instance
        """
        if cls._instance is None:
            cls._instance = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return cls._instance


async def get_supabase_client() -> AsyncGenerator[Client, None]:
    """
    Dependency for getting a Supabase client.

    Yields:
        Supabase Client
    """
    client = SupabaseManager.get_client()
    try:
        yield client
    finally:
        # Close or cleanup if needed in future
        pass
