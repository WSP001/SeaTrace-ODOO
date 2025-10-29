"""Configuration management for DeckSide service"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """DeckSide service configuration"""
    
    # Service identity
    service_name: str = "deckside"
    service_version: str = "1.0.0"
    port: int = 8002
    
    # Dependencies (other pillars)
    seaside_url: str = "http://localhost:8001"
    dockside_url: Optional[str] = "http://localhost:8003"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    # Timeouts
    upstream_timeout: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
