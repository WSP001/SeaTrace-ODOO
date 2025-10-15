"""
🛡️ DEFENSIVE LAYER 6: TLS/HTTPS ENCRYPTION
Blocks: Man-in-the-Middle, Eavesdropping
For the Commons Good!
"""

import ssl
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def create_ssl_context(
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None,
    min_version: ssl.TLSVersion = ssl.TLSVersion.TLSv1_3
) -> ssl.SSLContext:
    """
    Create SSL context with strong security settings
    
    Args:
        certfile: Path to certificate file
        keyfile: Path to private key file
        min_version: Minimum TLS version (default: TLS 1.3)
        
    Returns:
        Configured SSL context
    """
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Set minimum TLS version
    context.minimum_version = min_version
    
    # Disable weak ciphers
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    
    # Load certificate and key if provided
    if certfile and keyfile:
        try:
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            logger.info(f"SSL context loaded with cert: {certfile}")
        except Exception as e:
            logger.error(f"Failed to load SSL certificate: {e}")
            raise
    else:
        logger.warning("No SSL certificate provided. HTTPS will not be available.")
    
    # Additional security options
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1
    context.options |= ssl.OP_SINGLE_DH_USE
    context.options |= ssl.OP_SINGLE_ECDH_USE
    
    return context

def get_uvicorn_ssl_config(
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None
) -> dict:
    """
    Get SSL configuration for Uvicorn
    
    Args:
        certfile: Path to certificate file
        keyfile: Path to private key file
        
    Returns:
        Dictionary with SSL configuration for Uvicorn
    """
    if not certfile or not keyfile:
        logger.warning("No SSL certificates provided. Running without HTTPS.")
        return {}
    
    return {
        'ssl_keyfile': keyfile,
        'ssl_certfile': certfile,
        'ssl_version': ssl.PROTOCOL_TLS_SERVER,
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
    }

# HTTPS redirect middleware
from fastapi import Request
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to redirect HTTP to HTTPS"""
    
    async def dispatch(self, request: Request, call_next):
        # Check if request is HTTP (not HTTPS)
        if request.url.scheme == "http":
            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)
        
        # Continue with HTTPS request
        response = await call_next(request)
        return response
