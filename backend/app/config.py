from typing import List, Optional, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    TRUSTSHIELD_AI_ROOT: Optional[str] = None
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    MAX_WS_MESSAGE_BYTES: int = 1_048_576      # 1 MB default
    MAX_WS_TEXT_LENGTH: int = 10_000          # 10,000 chars default
    MAX_AUDIO_CHUNK_BYTES: int = 1_048_576     # 1 MB default per chunk
    MAX_SESSION_AUDIO_BYTES: int = 10_485_760  # 10 MB default per session
    TARGET_SAMPLE_RATE: int = 16_000          # 16 kHz
    TARGET_CHANNELS: int = 1                  # Mono
    TARGET_SAMPLE_WIDTH: int = 2              # 16-bit PCM
    MAX_AUDIO_DURATION_SECONDS: float = 300.0 # 5 minutes max per segment
    WHISPER_MODEL_SIZE: str = "tiny"          # Default Whisper model size

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
