from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PORT: Optional[int] = 8008
    IP_MEDIA_MTX: Optional[str] = "localhost"
    PORT_MEDIA_MTX: Optional[int] = 8554

    DAHUA_USERNAME: Optional[str] = "system"
    DAHUA_PASSWORD: Optional[str] = "Oryza@123"
    DAHUA_URL_BASE: Optional[str] = "http://192.168.105.15:8000"



settings = Settings()
