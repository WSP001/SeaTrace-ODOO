"""Configuration management for DockSide service"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """DockSide service configuration"""
    
    # Service identity
    service_name: str = "dockside"
    service_version: str = "1.0.0"
    port: int = 8003
    
    # Dependencies (other pillars)
    deckside_url: str = "http://localhost:8002"
    marketside_url: Optional[str] = "http://localhost:8004"
    
    # Database (Phase 1: in-memory, Phase 2: PostgreSQL)
    storage_mode: str = "memory"  # memory or postgres
    postgres_url: Optional[str] = "postgresql://user:pass@localhost:5432/seatrace"
    
    # Storage limits
    max_storage_items: int = 10000  # Memory storage limit
    retention_days: int = 90  # Data retention period
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Timeouts
    upstream_timeout: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
