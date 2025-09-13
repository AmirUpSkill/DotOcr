from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Get the absolute path to the backend directory
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    """
        Core Application Settings
    """
    # ---- Mistral AI API Configuration ---
    MISTRAL_API_KEY: str = ""
    
    # --- MinIO (Object Storage) Configuration --- 
    MINIO_ENDPOINT: str = "localhost:9002"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_NAME: str = "documents"
    
    # --- Model Configuration ---
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), 
        case_sensitive=False, 
        extra='ignore'
    )

settings = Settings()
