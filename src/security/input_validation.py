"""
🛡️ DEFENSIVE LAYER 2: INPUT VALIDATION
Blocks: SQL Injection, XSS, Command Injection
For the Commons Good!
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, Any
import re
import html

class SecureInput(BaseModel):
    """Base model with automatic input sanitization"""
    
    @validator('*', pre=True)
    def sanitize_input(cls, v: Any) -> Any:
        """Sanitize all string inputs"""
        if isinstance(v, str):
            return sanitize_string(v)
        return v

def sanitize_string(value: str, max_length: int = 10000) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return value
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Remove potential SQL injection patterns
    dangerous_patterns = [
        r'(\bOR\b|\bAND\b).*?=.*?',  # SQL OR/AND
        r';\s*DROP\s+TABLE',          # DROP TABLE
        r';\s*DELETE\s+FROM',         # DELETE FROM
        r'UNION\s+SELECT',            # UNION SELECT
        r'<script[^>]*>.*?</script>', # Script tags
        r'javascript:',               # JavaScript protocol
        r'on\w+\s*=',                 # Event handlers
    ]
    
    for pattern in dangerous_patterns:
        value = re.sub(pattern, '', value, flags=re.IGNORECASE)
    
    return value.strip()

class LicenseKeyInput(BaseModel):
    """Validated license key input"""
    license_key: str = Field(..., regex=r'^[A-Za-z0-9\-]{36}$')
    
    @validator('license_key')
    def validate_uuid_format(cls, v: str) -> str:
        """Ensure license key is valid UUID format"""
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.IGNORECASE):
            raise ValueError('License key must be valid UUID format')
        return v.lower()

class UserInput(BaseModel):
    """Validated user input"""
    user_id: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @validator('user_id', 'email')
    def sanitize_user_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize user fields"""
        if v:
            return sanitize_string(v, max_length=100)
        return v
