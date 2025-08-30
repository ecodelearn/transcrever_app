"""
⚙️ Configurações da aplicação
"""

import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações básicas
    APP_NAME: str = "Transcritor API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://legenda.iaforte.com.br"
    ]
    
    # Hugging Face
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Whisper Configuration
    WHISPER_MODEL_DEFAULT: str = os.getenv("WHISPER_MODEL", "medium")
    WHISPER_DEVICE: str = "cuda" if os.getenv("CUDA_AVAILABLE", "true").lower() == "true" else "cpu"
    
    # PyAnnote Configuration
    ENABLE_DIARIZATION_DEFAULT: bool = os.getenv("ENABLE_DIARIZATION", "true").lower() == "true"
    DIARIZATION_MODEL: str = "pyannote/speaker-diarization-3.1"
    
    # File Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "500"))  # MB
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [
        ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg",
        ".mp4", ".avi", ".mkv", ".mov", ".wmv"
    ]
    
    # Storage Paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    RESULTS_DIR: str = os.getenv("RESULTS_DIR", "results")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    
    # Processing
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
    JOB_TIMEOUT: int = int(os.getenv("JOB_TIMEOUT", "3600"))  # seconds
    
    # Language Settings
    DEFAULT_LANGUAGE: str = "pt"
    SUPPORTED_LANGUAGES: List[str] = [
        "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh"
    ]
    
    # Database (para futuro)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transcritor.db")
    
    # Redis (para futuro)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Performance tuning para RTX 3060
    TORCH_THREADS: int = int(os.getenv("TORCH_THREADS", "4"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "16"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Configurações específicas por ambiente
class DevelopmentConfig(Settings):
    """Configurações para desenvolvimento."""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Usar modelos menores em desenvolvimento se necessário
    WHISPER_MODEL_DEFAULT: str = "medium"  # RTX 3060 aguenta medium tranquilo
    MAX_CONCURRENT_JOBS: int = 2


class ProductionConfig(Settings):
    """Configurações para produção."""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Modelos maiores em produção
    WHISPER_MODEL_DEFAULT: str = "large"
    MAX_CONCURRENT_JOBS: int = 4


def get_config_by_env(env: str = None) -> Settings:
    """Get configuration by environment."""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()