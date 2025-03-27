from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application configuration settings."""

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Application Settings
    ALLOWED_ORIGINS: str
    DEBUG: bool = False

    # Security Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    NFC_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_SECRET_KEY: str

    # Additional Settings
    MAX_PROFILES_PER_USER: int = 4

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Environment-specific settings
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
