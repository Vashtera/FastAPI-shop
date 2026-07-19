from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


'''
Это путь к корневой папке backend проекта, вычисленный автоматически 
независимо от того, откуда ты запускаешь скрипт.
'''
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "FastAPI Shop"
    debug: bool = True
    database_url: str 
    redis_url: str
    cache_ttl_seconds: int
    cache_tasks_key: str
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    static_dir: str = "static"
    images_dir: str = "static/images"


settings = Settings() # type: ignore[call-arg] # Загружаются из .env файла