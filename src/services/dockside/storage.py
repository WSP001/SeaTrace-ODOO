"""Storage layer for DockSide service"""
import structlog
from typing import Dict, List, Optional
from datetime import datetime
from .models import StoredPacket, QueryRequest
from .config import settings

logger = structlog.get_logger()


class InMemoryStorage:
    """In-memory storage for packets (Phase 1)"""
    
    def __init__(self):
        self._storage: Dict[str, StoredPacket] = {}
        logger.info("in_memory_storage_initialized", max_items=settings.max_storage_items)
    
    async def store(self, packet: StoredPacket) -> bool:
        """Store a packet"""
        try:
            if len(self._storage) >= settings.max_storage_items:
                logger.warning(
                    "storage_limit_reached",
                    current_count=len(self._storage),
                    limit=settings.max_storage_items
                )
                return False
            
            self._storage[packet.packet_id] = packet
            logger.info(
                "packet_stored",
                packet_id=packet.packet_id,
                vessel_id=packet.vessel_id,
                total_stored=len(self._storage)
            )
            return True
            
        except Exception as e:
            logger.error("storage_error", error=str(e), packet_id=packet.packet_id)
            return False
    
    async def retrieve(self, packet_id: str) -> Optional[StoredPacket]:
        """Retrieve a packet by ID"""
        packet = self._storage.get(packet_id)
        if packet:
            logger.info("packet_retrieved", packet_id=packet_id)
        else:
            logger.info("packet_not_found", packet_id=packet_id)
        return packet
    
    async def query(self, query: QueryRequest) -> List[StoredPacket]:
        """Query packets with filters"""
        results = list(self._storage.values())
        
        # Apply filters
        if query.vessel_id:
            results = [p for p in results if p.vessel_id == query.vessel_id]
        
        if query.species:
            results = [p for p in results if p.species == query.species]
        
        if query.date_from:
            results = [p for p in results if p.stored_at >= query.date_from]
        
        if query.date_to:
            results = [p for p in results if p.stored_at <= query.date_to]
        
        if query.verified_only:
            results = [p for p in results if p.verified]
        
        # Sort by stored_at descending (newest first)
        results.sort(key=lambda p: p.stored_at, reverse=True)
        
        # Apply pagination
        total = len(results)
        results = results[query.offset:query.offset + query.limit]
        
        logger.info(
            "query_executed",
            total_matches=total,
            returned=len(results),
            filters={
                "vessel_id": query.vessel_id,
                "species": query.species,
                "verified_only": query.verified_only
            }
        )
        
        return results
    
    async def get_stats(self) -> Dict:
        """Get storage statistics"""
        packets = list(self._storage.values())
        
        if not packets:
            return {
                "total_packets": 0,
                "verified_packets": 0,
                "unverified_packets": 0,
                "total_catch_weight": 0.0,
                "species_breakdown": {},
                "storage_utilization": 0.0,
                "oldest_packet_date": None,
                "newest_packet_date": None
            }
        
        verified = [p for p in packets if p.verified]
        species_breakdown = {}
        total_weight = 0.0
        
        for packet in packets:
            species_breakdown[packet.species] = species_breakdown.get(packet.species, 0) + 1
            total_weight += packet.catch_weight
        
        dates = [p.stored_at for p in packets]
        
        return {
            "total_packets": len(packets),
            "verified_packets": len(verified),
            "unverified_packets": len(packets) - len(verified),
            "total_catch_weight": round(total_weight, 2),
            "species_breakdown": species_breakdown,
            "storage_utilization": round((len(packets) / settings.max_storage_items) * 100, 2),
            "oldest_packet_date": min(dates) if dates else None,
            "newest_packet_date": max(dates) if dates else None
        }
    
    async def count(self) -> int:
        """Get total packet count"""
        return len(self._storage)
    
    async def clear_all(self) -> int:
        """Clear all storage (for testing)"""
        count = len(self._storage)
        self._storage.clear()
        logger.warning("storage_cleared", packets_deleted=count)
        return count


# Global storage instance
storage = InMemoryStorage()
