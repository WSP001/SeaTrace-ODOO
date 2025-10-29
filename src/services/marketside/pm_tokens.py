"""PM Token verification for MarketSide service"""
import structlog
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()


class PMTokenManager:
    """Manages PM Token verification for investor/endorser access"""
    
    # Proceeding Master Tokens - Demo/Development
    VALID_TOKENS = {
        "PM-SEAS-2024-001": {
            "access_level": "Fisheries Digital Monitoring",
            "pillars": ["seaside"],
            "role": "fisheries_monitor",
            "expires": None  # No expiry for demo
        },
        "PM-DECK-2024-002": {
            "access_level": "Seafood Contributors",
            "pillars": ["seaside", "deckside"],
            "role": "contributor",
            "expires": None
        },
        "PM-DOCK-2024-003": {
            "access_level": "Business Managers",
            "pillars": ["seaside", "deckside", "dockside"],
            "role": "manager",
            "expires": None
        },
        "PM-MARK-2024-004": {
            "access_level": "Investors (Full Access)",
            "pillars": ["seaside", "deckside", "dockside", "marketside"],
            "role": "investor",
            "expires": None
        }
    }
    
    def __init__(self):
        logger.info("pm_token_manager_initialized", total_tokens=len(self.VALID_TOKENS))
    
    async def verify_token(self, token: str) -> Dict:
        """Verify PM token and return access details"""
        try:
            if token in self.VALID_TOKENS:
                token_data = self.VALID_TOKENS[token]
                
                logger.info(
                    "pm_token_verified",
                    token=token[:10] + "***",  # Partial token for logging
                    access_level=token_data["access_level"]
                )
                
                return {
                    "valid": True,
                    "token": token,
                    "access_level": token_data["access_level"],
                    "pillar_access": token_data["pillars"],
                    "role": token_data["role"],
                    "dashboard_url": "/dashboard",
                    "expires_at": token_data["expires"]
                }
            else:
                logger.warning("pm_token_invalid", token=token[:10] + "***")
                return {
                    "valid": False,
                    "token": token,
                    "access_level": None,
                    "pillar_access": [],
                    "dashboard_url": None,
                    "expires_at": None
                }
                
        except Exception as e:
            logger.error("pm_token_verification_error", error=str(e))
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def list_tokens(self) -> List[Dict]:
        """List all available PM tokens (for demo purposes)"""
        return [
            {
                "token": token,
                "access_level": data["access_level"],
                "pillars": data["pillars"],
                "role": data["role"]
            }
            for token, data in self.VALID_TOKENS.items()
        ]
    
    async def get_stats(self) -> Dict:
        """Get PM token statistics"""
        return {
            "total_tokens": len(self.VALID_TOKENS),
            "roles": list(set(data["role"] for data in self.VALID_TOKENS.values())),
            "access_levels": list(set(data["access_level"] for data in self.VALID_TOKENS.values()))
        }


# Global PM token manager instance
pm_token_manager = PMTokenManager()
