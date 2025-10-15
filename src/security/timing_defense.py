"""
🛡️ DEFENSIVE LAYER 3: TIMING ATTACK DEFENSE
Blocks: Timing Attacks, Side-Channel Attacks
For the Commons Good!
"""

import hmac
import asyncio
import secrets
from typing import Union

async def constant_time_compare(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
    """
    Constant-time string comparison to prevent timing attacks
    
    Args:
        a: First value to compare
        b: Second value to compare
        
    Returns:
        True if values match, False otherwise
    """
    # Convert to bytes if strings
    if isinstance(a, str):
        a = a.encode('utf-8')
    if isinstance(b, str):
        b = b.encode('utf-8')
    
    # Add random delay before comparison (0.5-2ms)
    delay = 0.0005 + (secrets.randbelow(1500) / 1000000)
    await asyncio.sleep(delay)
    
    # Use constant-time comparison
    result = hmac.compare_digest(a, b)
    
    # Add random delay after comparison (0.5-2ms)
    delay = 0.0005 + (secrets.randbelow(1500) / 1000000)
    await asyncio.sleep(delay)
    
    return result

async def verify_signature_constant_time(
    payload: str,
    signature: str,
    secret_key: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Verify HMAC signature with constant-time comparison
    
    Args:
        payload: Data that was signed
        signature: Signature to verify
        secret_key: Secret key used for signing
        algorithm: Hash algorithm (default: sha256)
        
    Returns:
        True if signature is valid, False otherwise
    """
    # Calculate expected signature
    expected = hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        algorithm
    ).hexdigest()
    
    # Use constant-time comparison
    return await constant_time_compare(signature, expected)

def add_timing_jitter(base_delay_ms: float = 1.0, jitter_ms: float = 2.0) -> float:
    """
    Add random jitter to timing to prevent timing analysis
    
    Args:
        base_delay_ms: Base delay in milliseconds
        jitter_ms: Maximum additional jitter in milliseconds
        
    Returns:
        Total delay in seconds
    """
    jitter = secrets.randbelow(int(jitter_ms * 1000)) / 1000000
    return (base_delay_ms / 1000) + jitter
