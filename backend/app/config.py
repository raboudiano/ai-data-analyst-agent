from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "AI Data Analyst Agent"
    cors_origins: str = "http://localhost:3000"
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    max_upload_size_mb: int = 20
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

settings = Settings()
