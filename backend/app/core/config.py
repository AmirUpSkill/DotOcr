from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
        Core Application Settings
    """
    # ---- Mistral AI API Configuration ---
    MISTRAL_API_KEY: str = ""
    
    # --- MinIO (Object Storage) Configuration --- 
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_NAME: str = "documents"
    
    # --- Model Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=False, 
        extra='ignore'
    )

settings = Settings()
