"""
🛡️ DEFENSIVE LAYER 5: SECRET MANAGEMENT
Blocks: Secret Leakage, Credential Exposure
For the Commons Good!
"""

import os
from typing import Optional, Dict
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    """Manages secrets with encryption at rest"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize secret manager
        
        Args:
            encryption_key: Base64-encoded Fernet key (generated if not provided)
        """
        if encryption_key is None:
            encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if encryption_key:
            try:
                self.cipher = Fernet(encryption_key.encode('utf-8'))
                logger.info("SecretManager initialized with provided key")
            except Exception as e:
                logger.warning(f"Invalid encryption key: {e}. Using unencrypted mode.")
                self.cipher = None
        else:
            logger.warning("No encryption key provided. Secrets will not be encrypted!")
            self.cipher = None
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from environment
        
        Args:
            secret_name: Name of the secret
            default: Default value if secret not found
            
        Returns:
            Decrypted secret value or default
        """
        encrypted_value = os.getenv(secret_name)
        
        if not encrypted_value:
            if default is not None:
                logger.debug(f"Secret '{secret_name}' not found, using default")
                return default
            logger.warning(f"Secret '{secret_name}' not found and no default provided")
            return None
        
        # If no cipher, return raw value (development mode)
        if self.cipher is None:
            return encrypted_value
        
        # Decrypt secret
        try:
            decrypted = self.cipher.decrypt(encrypted_value.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decrypt secret '{secret_name}': {e}")
            return default
    
    def encrypt_secret(self, value: str) -> str:
        """
        Encrypt a secret value
        
        Args:
            value: Plain text secret
            
        Returns:
            Encrypted secret (base64 encoded)
        """
        if self.cipher is None:
            logger.warning("No cipher available, returning plain text")
            return value
        
        encrypted = self.cipher.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet encryption key"""
        key = Fernet.generate_key()
        return key.decode('utf-8')

# Global secret manager instance
secret_manager = SecretManager()

def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get secret
    
    Args:
        name: Secret name
        default: Default value if not found
        
    Returns:
        Secret value or default
    """
    return secret_manager.get_secret(name, default)

# Common secrets with safe defaults for development
JWT_SECRET_KEY = get_secret('JWT_SECRET_KEY', 'dev-secret-change-in-production')
DATABASE_URL = get_secret('DATABASE_URL', 'sqlite:///./seatrace.db')
REDIS_URL = get_secret('REDIS_URL', 'redis://localhost:6379/0')
API_KEY = get_secret('API_KEY', 'dev-api-key')
