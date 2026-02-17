from __future__ import annotations

import json
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve .env relative to this file → backend/.env
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    use_mock: bool = True
    model_name: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 100
    max_rows_per_file: int = 500_000
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
