from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings management using Pydantic.
    This centralizes our configuration and provides validation.
    """
    DATABASE_URL: str = "postgresql+asyncpg://assetuser:assetpass@localhost:5432/asset_manager"
    UPLOAD_FOLDER: str = "./uploads"
    ENVIRONMENT: str = "development"
    
    # New Relic settings (optional for now)
    NEW_RELIC_LICENSE_KEY: str = ""
    NEW_RELIC_APP_NAME: str = "home-asset-manager"

    class Config:
        env_file = ".env"

# Create a global settings instance
settings = Settings()