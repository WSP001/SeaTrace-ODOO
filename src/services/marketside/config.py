"""Configuration management for MarketSide service"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """MarketSide service configuration"""
    
    # Service identity
    service_name: str = "marketside"
    service_version: str = "1.0.0"
    port: int = 8004
    
    # Dependencies (other pillars)
    dockside_url: str = "http://localhost:8003"
    
    # Security (PRIVATE KEY OUTGOING)
    private_key_path: Optional[str] = None  # Path to private key for signing
    public_key_path: Optional[str] = None   # Path to public key for verification
    
    # PM Token verification
    enable_pm_tokens: bool = True
    pm_token_db_url: Optional[str] = None  # Future: database for tokens
    
    # Market exchange
    enable_market_exchange: bool = True
    exchange_rate_limit: int = 100  # Requests per minute
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Timeouts
    upstream_timeout: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
