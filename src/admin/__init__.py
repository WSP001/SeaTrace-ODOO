"""Admin API endpoints for SeaTrace-ODOO.

This module provides secure administrative endpoints for:
- CRL (Certificate Revocation List) management
- License inspection and auditing
- System health and performance monitoring

All endpoints require admin authentication via Ed25519 signed tokens.
"""

__version__ = "0.1.0"
