"""Market data publisher for MarketSide service"""
import structlog
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import json

logger = structlog.get_logger()


class MarketPublisher:
    """Publishes data to external markets with PRIVATE KEY OUTGOING"""
    
    def __init__(self):
        self._published_items: Dict[str, Dict] = {}
        logger.info("market_publisher_initialized")
    
    async def publish_listing(self, packet_id: str, data: Dict) -> Dict:
        """Publish product listing to market"""
        try:
            listing_id = f"listing-{packet_id}"
            
            listing = {
                "listing_id": listing_id,
                "packet_id": packet_id,
                "data": data,
                "status": "active",
                "published_at": datetime.utcnow().isoformat(),
                "type": "listing"
            }
            
            self._published_items[listing_id] = listing
            
            logger.info(
                "listing_published",
                listing_id=listing_id,
                packet_id=packet_id
            )
            
            return {
                "success": True,
                "listing_id": listing_id,
                "market_url": f"/market/listings/{listing_id}"
            }
            
        except Exception as e:
            logger.error("listing_publication_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def publish_transaction(self, packet_id: str, data: Dict) -> Dict:
        """Publish transaction to market"""
        try:
            transaction_id = f"tx-{packet_id}"
            
            transaction = {
                "transaction_id": transaction_id,
                "packet_id": packet_id,
                "data": data,
                "status": "completed",
                "published_at": datetime.utcnow().isoformat(),
                "type": "transaction"
            }
            
            self._published_items[transaction_id] = transaction
            
            logger.info(
                "transaction_published",
                transaction_id=transaction_id,
                packet_id=packet_id
            )
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "market_url": f"/market/transactions/{transaction_id}"
            }
            
        except Exception as e:
            logger.error("transaction_publication_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def issue_certificate(
        self,
        packet_id: str,
        vessel_id: str,
        traceability_chain: List[Dict]
    ) -> Dict:
        """Issue traceability certificate with PRIVATE KEY OUTGOING signature"""
        try:
            certificate_id = f"cert-{packet_id}"
            
            # Create certificate data
            certificate = {
                "certificate_id": certificate_id,
                "packet_id": packet_id,
                "vessel_id": vessel_id,
                "traceability_chain": traceability_chain,
                "issued_at": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "issuer": "SeaTrace-ODOO MarketSide",
                "type": "certificate"
            }
            
            # Generate signature (PRIVATE KEY OUTGOING)
            # In production: use PacketCryptoHandler with private key
            certificate_json = json.dumps(certificate, sort_keys=True)
            signature = hashlib.sha256(certificate_json.encode()).hexdigest()
            certificate["signature"] = signature
            
            self._published_items[certificate_id] = certificate
            
            logger.info(
                "certificate_issued",
                certificate_id=certificate_id,
                packet_id=packet_id,
                vessel_id=vessel_id
            )
            
            return {
                "success": True,
                "certificate_id": certificate_id,
                "signature": signature,
                "valid_until": certificate["valid_until"]
            }
            
        except Exception as e:
            logger.error("certificate_issuance_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_stats(self) -> Dict:
        """Get market publishing statistics"""
        items = list(self._published_items.values())
        
        listings = [i for i in items if i.get("type") == "listing"]
        transactions = [i for i in items if i.get("type") == "transaction"]
        certificates = [i for i in items if i.get("type") == "certificate"]
        
        return {
            "total_listings": len(listings),
            "total_transactions": len(transactions),
            "total_certificates": len(certificates),
            "total_published": len(items)
        }
    
    async def get_item(self, item_id: str) -> Optional[Dict]:
        """Retrieve published item by ID"""
        return self._published_items.get(item_id)


# Global publisher instance
publisher = MarketPublisher()
