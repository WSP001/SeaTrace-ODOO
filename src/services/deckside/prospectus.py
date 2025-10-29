"""
DeckSide Prospectus Function - Core Investor IP
Track 2 (Private Key): $CHECK KEY Calculation

CRITICAL: This is THE core algorithmic value proposition for investors.
The prospectus function calculates immutable financial projections at-sea,
BEFORE landing, enabling predictive revenue tracking and ML model training.

Author: Acting Master (Strategic Optimization)
Date: 2025-10-16
License: LICENSE.limited (Private Key - Monetized)
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Dict, Optional
import structlog
import uuid

logger = structlog.get_logger()


class ProspectusCalculator:
    """
    CRITICAL: Calculate $CHECK KEY (immutable financial projection)
    
    This is the 'predictive hand' that creates investor value by
    projecting revenue BEFORE landing (at-sea financial projection).
    
    The $CHECK KEY is the first immutable financial record in the chain:
    SeaSide (PACKET_ID) → DeckSide ($CHECK KEY) → DockSide (Consensus Block) → MarketSide (Settlement)
    """
    
    # Precision settings for financial calculations
    DECIMAL_PRECISION = Decimal('0.01')  # $0.01 USD precision
    
    # Business rules
    MIN_CATCH_KG = Decimal('0.1')
    MAX_CATCH_KG = Decimal('1000000')
    MIN_PRICE_PER_KG = Decimal('0.01')
    MAX_PRICE_PER_KG = Decimal('10000')
    
    @staticmethod
    def calculate_check_key(
        estimated_catch_kg: float,
        projected_ground_price_usd_per_kg: float,
        species: str,
        vessel_id: str,
        correlation_id: Optional[str] = None,
        packet_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate $CHECK KEY = estimated_catch × projected_ground_price
        
        This is THE first immutable financial projection in the chain.
        Once created, this value cannot be modified - only reconciled against
        actual landed value in DockSide.
        
        Args:
            estimated_catch_kg: Captain's estimated catch weight (kg) from at-sea observation
            projected_ground_price_usd_per_kg: Market price projection at time of catch
            species: Species code (for price verification and market data enrichment)
            vessel_id: Vessel identifier (links to SeaSide PACKET_ID)
            correlation_id: Optional correlation ID (generated if not provided)
            packet_id: Optional packet ID from SeaSide (links to upstream PING data)
            metadata: Optional metadata (fishing area, gear type, quality grade, etc.)
        
        Returns:
            dict with $CHECK KEY and complete projection metadata
            
        Raises:
            ValueError: If inputs violate business rules
            
        Example:
            >>> calc = ProspectusCalculator()
            >>> result = calc.calculate_check_key(
            ...     estimated_catch_kg=500.0,
            ...     projected_ground_price_usd_per_kg=15.00,
            ...     species="Tuna",
            ...     vessel_id="WSP-001"
            ... )
            >>> print(result["check_key_usd"])
            7500.00
        """
        # Generate IDs if not provided
        correlation_id = correlation_id or str(uuid.uuid4())
        packet_id = packet_id or f"DECKSIDE-{str(uuid.uuid4())}"
        
        # Convert to Decimal for financial precision
        try:
            catch = Decimal(str(estimated_catch_kg))
            price = Decimal(str(projected_ground_price_usd_per_kg))
        except Exception as e:
            logger.error(
                "prospectus_decimal_conversion_failed",
                estimated_catch_kg=estimated_catch_kg,
                projected_price=projected_ground_price_usd_per_kg,
                error=str(e),
                correlation_id=correlation_id
            )
            raise ValueError(f"Invalid numeric input: {e}")
        
        # Validate business rules
        ProspectusCalculator._validate_inputs(catch, price, species, vessel_id)
        
        # Core calculation: $CHECK KEY = catch × price
        check_key_usd = (catch * price).quantize(
            ProspectusCalculator.DECIMAL_PRECISION,
            rounding=ROUND_HALF_UP
        )
        
        # Create immutable projection packet
        timestamp = datetime.now(timezone.utc)
        
        projection = {
            # Core financial projection
            "check_key_usd": float(check_key_usd),
            "estimated_catch_kg": float(catch),
            "projected_price_per_kg_usd": float(price),
            
            # Identity and traceability
            "species": species,
            "vessel_id": vessel_id,
            "packet_id": packet_id,
            "correlation_id": correlation_id,
            
            # Timestamp (ISO 8601 with UTC)
            "projection_timestamp": timestamp.isoformat(),
            "projection_epoch": int(timestamp.timestamp()),
            
            # Immutability flag
            "immutable": True,  # This value cannot be changed post-creation
            "immutability_hash": None,  # Placeholder for blockchain integration
            
            # License and access control
            "track": "PRIVATE_KEY",  # Track 2 - Investor monetization
            "license_required": "LIMITED",  # Requires Private Key license
            
            # Workflow routing
            "source_service": "deckside",
            "next_step": "dockside_reconciliation",
            "next_service": "dockside",
            
            # Optional metadata
            "metadata": metadata or {}
        }
        
        # Add calculation metadata
        projection["calculation"] = {
            "formula": "estimated_catch_kg × projected_price_per_kg_usd",
            "precision": "0.01 USD",
            "rounding": "ROUND_HALF_UP",
            "decimal_places": 2
        }
        
        logger.info(
            "prospectus_check_key_calculated",
            vessel_id=vessel_id,
            species=species,
            check_key_usd=float(check_key_usd),
            estimated_catch_kg=float(catch),
            projected_price_usd=float(price),
            correlation_id=correlation_id,
            track="PRIVATE_KEY",
            packet_id=packet_id
        )
        
        return projection
    
    @staticmethod
    def _validate_inputs(
        catch: Decimal,
        price: Decimal,
        species: str,
        vessel_id: str
    ) -> None:
        """
        Validate inputs against business rules.
        
        Raises:
            ValueError: If inputs violate business rules
        """
        # Validate catch weight
        if catch < ProspectusCalculator.MIN_CATCH_KG:
            raise ValueError(
                f"Catch weight {catch} kg below minimum "
                f"({ProspectusCalculator.MIN_CATCH_KG} kg)"
            )
        
        if catch > ProspectusCalculator.MAX_CATCH_KG:
            raise ValueError(
                f"Catch weight {catch} kg exceeds maximum "
                f"({ProspectusCalculator.MAX_CATCH_KG} kg)"
            )
        
        # Validate price
        if price < ProspectusCalculator.MIN_PRICE_PER_KG:
            raise ValueError(
                f"Price {price} USD/kg below minimum "
                f"({ProspectusCalculator.MIN_PRICE_PER_KG} USD/kg)"
            )
        
        if price > ProspectusCalculator.MAX_PRICE_PER_KG:
            raise ValueError(
                f"Price {price} USD/kg exceeds maximum "
                f"({ProspectusCalculator.MAX_PRICE_PER_KG} USD/kg)"
            )
        
        # Validate species (non-empty string)
        if not species or not isinstance(species, str):
            raise ValueError(f"Species must be non-empty string, got: {species}")
        
        # Validate vessel ID (non-empty string)
        if not vessel_id or not isinstance(vessel_id, str):
            raise ValueError(f"Vessel ID must be non-empty string, got: {vessel_id}")
    
    @staticmethod
    def enrich_with_market_data(
        check_key: Dict,
        market_data: Dict
    ) -> Dict:
        """
        Enrich $CHECK KEY with real-time market intelligence.
        
        This is a PREMIUM feature for Track 2 (Private Key) subscribers.
        Adds spot price, historical averages, variance analysis, and confidence scoring.
        
        Args:
            check_key: $CHECK KEY projection from calculate_check_key()
            market_data: Real-time market data (spot price, 30d avg, variance, etc.)
        
        Returns:
            Enriched $CHECK KEY with market intelligence
            
        Example:
            >>> check_key = calc.calculate_check_key(500, 15.00, "Tuna", "WSP-001")
            >>> market_data = {
            ...     "spot_price": 15.25,
            ...     "avg_price_30d": 14.80,
            ...     "variance": 3.0,
            ...     "confidence": 0.92
            ... }
            >>> enriched = calc.enrich_with_market_data(check_key, market_data)
            >>> print(enriched["market_enrichment"]["price_differential_percent"])
            1.67
        """
        enriched = check_key.copy()
        
        # Calculate price differential
        projected_price = Decimal(str(check_key["projected_price_per_kg_usd"]))
        spot_price = Decimal(str(market_data.get("spot_price", 0)))
        
        if spot_price > 0:
            price_diff_percent = (
                ((spot_price - projected_price) / projected_price) * 100
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            price_diff_percent = Decimal('0.00')
        
        # Add market enrichment
        enriched["market_enrichment"] = {
            "current_spot_price_usd": float(spot_price),
            "30d_avg_price_usd": market_data.get("avg_price_30d"),
            "price_variance_percent": market_data.get("variance"),
            "price_differential_percent": float(price_diff_percent),
            "confidence_score": market_data.get("confidence", 0.85),
            "market_conditions": market_data.get("conditions", "unknown"),
            "enriched_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Recalculate $CHECK KEY with spot price (informational only)
        if spot_price > 0:
            catch = Decimal(str(check_key["estimated_catch_kg"]))
            spot_check_key = (catch * spot_price).quantize(
                ProspectusCalculator.DECIMAL_PRECISION,
                rounding=ROUND_HALF_UP
            )
            enriched["market_enrichment"]["spot_check_key_usd"] = float(spot_check_key)
        
        logger.info(
            "prospectus_market_enrichment_complete",
            vessel_id=check_key.get("vessel_id"),
            check_key_usd=check_key.get("check_key_usd"),
            spot_check_key_usd=enriched["market_enrichment"].get("spot_check_key_usd"),
            price_differential_percent=float(price_diff_percent),
            correlation_id=check_key.get("correlation_id")
        )
        
        return enriched
    
    @staticmethod
    def calculate_variance(
        check_key: Dict,
        actual_landed_value_usd: float
    ) -> Dict:
        """
        Calculate variance between $CHECK KEY projection and actual landed value.
        
        This variance is used to train the ML prediction model (DockSide reconciliation).
        
        Args:
            check_key: $CHECK KEY projection from calculate_check_key()
            actual_landed_value_usd: Actual revenue from DockSide fish ticket
        
        Returns:
            Variance analysis dict
            
        Example:
            >>> check_key = calc.calculate_check_key(500, 15.00, "Tuna", "WSP-001")
            >>> variance = calc.calculate_variance(check_key, 7800.00)
            >>> print(variance["variance_percent"])
            4.00
        """
        projected_value = Decimal(str(check_key["check_key_usd"]))
        actual_value = Decimal(str(actual_landed_value_usd))
        
        # Calculate absolute and percentage variance
        variance_usd = actual_value - projected_value
        
        if projected_value > 0:
            variance_percent = (
                (variance_usd / projected_value) * 100
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            variance_percent = Decimal('0.00')
        
        # Determine accuracy classification
        abs_variance_percent = abs(variance_percent)
        if abs_variance_percent <= 5:
            accuracy = "excellent"
        elif abs_variance_percent <= 10:
            accuracy = "good"
        elif abs_variance_percent <= 20:
            accuracy = "acceptable"
        else:
            accuracy = "poor"
        
        variance_analysis = {
            "projected_value_usd": float(projected_value),
            "actual_landed_value_usd": float(actual_value),
            "variance_usd": float(variance_usd),
            "variance_percent": float(variance_percent),
            "accuracy_classification": accuracy,
            "within_5_percent": abs_variance_percent <= 5,
            "within_10_percent": abs_variance_percent <= 10,
            "correlation_id": check_key.get("correlation_id"),
            "vessel_id": check_key.get("vessel_id"),
            "species": check_key.get("species"),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            "prospectus_variance_calculated",
            vessel_id=check_key.get("vessel_id"),
            projected_value_usd=float(projected_value),
            actual_value_usd=float(actual_value),
            variance_percent=float(variance_percent),
            accuracy=accuracy,
            correlation_id=check_key.get("correlation_id")
        )
        
        return variance_analysis


# Convenience function for quick calculations
def quick_check_key(
    catch_kg: float,
    price_per_kg: float,
    species: str = "Unknown",
    vessel_id: str = "UNKNOWN"
) -> float:
    """
    Quick $CHECK KEY calculation (returns only the dollar value).
    
    For full metadata, use ProspectusCalculator.calculate_check_key()
    
    Example:
        >>> quick_check_key(500, 15.00)
        7500.00
    """
    result = ProspectusCalculator.calculate_check_key(
        estimated_catch_kg=catch_kg,
        projected_ground_price_usd_per_kg=price_per_kg,
        species=species,
        vessel_id=vessel_id
    )
    return result["check_key_usd"]
