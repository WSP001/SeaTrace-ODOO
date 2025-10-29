"""
Unit tests for DeckSide Prospectus Function
Tests the CRITICAL $CHECK KEY calculation logic
"""

import pytest
from decimal import Decimal
from datetime import datetime
from prospectus import (
    ProspectusCalculator,
    quick_check_key
)


class TestProspectusCalculator:
    """Test suite for ProspectusCalculator"""
    
    def test_basic_check_key_calculation(self):
        """Test basic $CHECK KEY calculation"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-001"
        )
        
        assert result["check_key_usd"] == 7500.00
        assert result["estimated_catch_kg"] == 500.0
        assert result["projected_price_per_kg_usd"] == 15.00
        assert result["species"] == "Tuna"
        assert result["vessel_id"] == "WSP-001"
        assert result["track"] == "PRIVATE_KEY"
        assert result["immutable"] is True
    
    def test_decimal_precision(self):
        """Test Decimal precision to $0.01 USD"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=123.456,
            projected_ground_price_usd_per_kg=12.345,
            species="Salmon",
            vessel_id="WSP-002"
        )
        
        # 123.456 × 12.345 = 1524.35052 → rounds to 1524.35
        assert result["check_key_usd"] == 1524.35
        assert result["calculation"]["precision"] == "0.01 USD"
        assert result["calculation"]["decimal_places"] == 2
    
    def test_correlation_id_generation(self):
        """Test correlation ID is generated if not provided"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=100.0,
            projected_ground_price_usd_per_kg=10.00,
            species="Cod",
            vessel_id="WSP-003"
        )
        
        assert "correlation_id" in result
        assert len(result["correlation_id"]) > 0
        assert result["packet_id"].startswith("DECKSIDE-")
    
    def test_custom_correlation_id(self):
        """Test custom correlation ID is preserved"""
        custom_corr_id = "TEST-CORRELATION-ID-123"
        custom_packet_id = "SEASIDE-PACKET-456"
        
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=200.0,
            projected_ground_price_usd_per_kg=20.00,
            species="Herring",
            vessel_id="WSP-004",
            correlation_id=custom_corr_id,
            packet_id=custom_packet_id
        )
        
        assert result["correlation_id"] == custom_corr_id
        assert result["packet_id"] == custom_packet_id
    
    def test_metadata_preservation(self):
        """Test optional metadata is preserved"""
        metadata = {
            "fishing_area": "FAO-67",
            "gear_type": "longline",
            "quality_grade": "A"
        }
        
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=300.0,
            projected_ground_price_usd_per_kg=25.00,
            species="Tuna",
            vessel_id="WSP-005",
            metadata=metadata
        )
        
        assert result["metadata"] == metadata
    
    def test_timestamp_format(self):
        """Test timestamp is ISO 8601 with UTC"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=150.0,
            projected_ground_price_usd_per_kg=18.00,
            species="Mackerel",
            vessel_id="WSP-006"
        )
        
        # Check ISO 8601 format
        timestamp = result["projection_timestamp"]
        assert "T" in timestamp
        assert timestamp.endswith(("Z", "+00:00"))
        
        # Check epoch timestamp
        assert isinstance(result["projection_epoch"], int)
        assert result["projection_epoch"] > 0
    
    def test_minimum_catch_validation(self):
        """Test minimum catch weight validation"""
        with pytest.raises(ValueError, match="below minimum"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=0.05,  # Below MIN_CATCH_KG (0.1)
                projected_ground_price_usd_per_kg=15.00,
                species="Tuna",
                vessel_id="WSP-007"
            )
    
    def test_maximum_catch_validation(self):
        """Test maximum catch weight validation"""
        with pytest.raises(ValueError, match="exceeds maximum"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=2000000.0,  # Above MAX_CATCH_KG (1,000,000)
                projected_ground_price_usd_per_kg=15.00,
                species="Tuna",
                vessel_id="WSP-008"
            )
    
    def test_minimum_price_validation(self):
        """Test minimum price validation"""
        with pytest.raises(ValueError, match="below minimum"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=500.0,
                projected_ground_price_usd_per_kg=0.005,  # Below MIN_PRICE_PER_KG (0.01)
                species="Sardine",
                vessel_id="WSP-009"
            )
    
    def test_maximum_price_validation(self):
        """Test maximum price validation"""
        with pytest.raises(ValueError, match="exceeds maximum"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=500.0,
                projected_ground_price_usd_per_kg=15000.0,  # Above MAX_PRICE_PER_KG (10,000)
                species="Tuna",
                vessel_id="WSP-010"
            )
    
    def test_invalid_species_validation(self):
        """Test species validation"""
        with pytest.raises(ValueError, match="Species must be non-empty string"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=500.0,
                projected_ground_price_usd_per_kg=15.00,
                species="",  # Empty species
                vessel_id="WSP-011"
            )
    
    def test_invalid_vessel_id_validation(self):
        """Test vessel ID validation"""
        with pytest.raises(ValueError, match="Vessel ID must be non-empty string"):
            ProspectusCalculator.calculate_check_key(
                estimated_catch_kg=500.0,
                projected_ground_price_usd_per_kg=15.00,
                species="Tuna",
                vessel_id=""  # Empty vessel ID
            )
    
    def test_market_data_enrichment(self):
        """Test market data enrichment (premium feature)"""
        check_key = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-012"
        )
        
        market_data = {
            "spot_price": 15.25,
            "avg_price_30d": 14.80,
            "variance": 3.0,
            "confidence": 0.92,
            "conditions": "favorable"
        }
        
        enriched = ProspectusCalculator.enrich_with_market_data(check_key, market_data)
        
        assert "market_enrichment" in enriched
        assert enriched["market_enrichment"]["current_spot_price_usd"] == 15.25
        assert enriched["market_enrichment"]["30d_avg_price_usd"] == 14.80
        assert enriched["market_enrichment"]["price_variance_percent"] == 3.0
        assert enriched["market_enrichment"]["confidence_score"] == 0.92
        assert enriched["market_enrichment"]["market_conditions"] == "favorable"
        
        # Check price differential calculation
        # (15.25 - 15.00) / 15.00 * 100 = 1.67%
        assert enriched["market_enrichment"]["price_differential_percent"] == 1.67
        
        # Check spot $CHECK KEY recalculation
        # 500 kg × 15.25 USD/kg = 7625.00 USD
        assert enriched["market_enrichment"]["spot_check_key_usd"] == 7625.00
    
    def test_variance_calculation(self):
        """Test variance calculation for ML model training"""
        check_key = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-013"
        )
        
        # Actual landed value: $7,800 (vs projected $7,500)
        variance = ProspectusCalculator.calculate_variance(check_key, 7800.00)
        
        assert variance["projected_value_usd"] == 7500.00
        assert variance["actual_landed_value_usd"] == 7800.00
        assert variance["variance_usd"] == 300.00
        assert variance["variance_percent"] == 4.00  # (300 / 7500) * 100
        assert variance["accuracy_classification"] == "excellent"  # ≤5%
        assert variance["within_5_percent"] is True
        assert variance["within_10_percent"] is True
    
    def test_variance_accuracy_classifications(self):
        """Test variance accuracy classification thresholds"""
        check_key = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=1000.0,
            projected_ground_price_usd_per_kg=10.00,
            species="Cod",
            vessel_id="WSP-014"
        )
        # Projected: $10,000
        
        # Excellent: ≤5% variance
        var_excellent = ProspectusCalculator.calculate_variance(check_key, 10400.00)
        assert var_excellent["accuracy_classification"] == "excellent"
        
        # Good: >5% and ≤10%
        var_good = ProspectusCalculator.calculate_variance(check_key, 10800.00)
        assert var_good["accuracy_classification"] == "good"
        
        # Acceptable: >10% and ≤20%
        var_acceptable = ProspectusCalculator.calculate_variance(check_key, 11500.00)
        assert var_acceptable["accuracy_classification"] == "acceptable"
        
        # Poor: >20%
        var_poor = ProspectusCalculator.calculate_variance(check_key, 13000.00)
        assert var_poor["accuracy_classification"] == "poor"
    
    def test_quick_check_key_convenience_function(self):
        """Test quick_check_key convenience function"""
        result = quick_check_key(500, 15.00)
        assert result == 7500.00
        
        result_with_species = quick_check_key(500, 15.00, "Tuna", "WSP-015")
        assert result_with_species == 7500.00
    
    def test_zero_division_safety(self):
        """Test zero division protection in variance calculation"""
        # Create check_key with zero value (edge case)
        check_key = {
            "check_key_usd": 0.00,
            "vessel_id": "WSP-016",
            "species": "Unknown",
            "correlation_id": "test-123"
        }
        
        variance = ProspectusCalculator.calculate_variance(check_key, 100.00)
        assert variance["variance_percent"] == 0.00  # Should not crash
    
    def test_negative_variance(self):
        """Test variance calculation when actual < projected"""
        check_key = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-017"
        )
        # Projected: $7,500, Actual: $7,000
        
        variance = ProspectusCalculator.calculate_variance(check_key, 7000.00)
        
        assert variance["variance_usd"] == -500.00
        assert variance["variance_percent"] == -6.67  # Negative variance
        assert variance["accuracy_classification"] == "good"  # Abs value ≤10%
    
    def test_immutability_fields(self):
        """Test immutability and blockchain integration fields"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-018"
        )
        
        assert result["immutable"] is True
        assert "immutability_hash" in result
        assert result["next_step"] == "dockside_reconciliation"
        assert result["next_service"] == "dockside"
    
    def test_license_and_track_metadata(self):
        """Test license and track metadata for access control"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=500.0,
            projected_ground_price_usd_per_kg=15.00,
            species="Tuna",
            vessel_id="WSP-019"
        )
        
        assert result["track"] == "PRIVATE_KEY"
        assert result["license_required"] == "LIMITED"
        assert result["source_service"] == "deckside"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_minimum_valid_inputs(self):
        """Test minimum valid input values"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=0.1,  # MIN_CATCH_KG
            projected_ground_price_usd_per_kg=0.01,  # MIN_PRICE_PER_KG
            species="A",
            vessel_id="X"
        )
        assert result["check_key_usd"] == 0.00  # 0.1 × 0.01 = 0.001 → rounds to 0.00
    
    def test_maximum_valid_inputs(self):
        """Test maximum valid input values"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=1000000.0,  # MAX_CATCH_KG
            projected_ground_price_usd_per_kg=10000.0,  # MAX_PRICE_PER_KG
            species="Bluefin Tuna",
            vessel_id="WSP-LARGE-001"
        )
        assert result["check_key_usd"] == 10000000000.00  # 1M kg × 10K USD/kg = 10B USD
    
    def test_float_to_decimal_conversion(self):
        """Test accurate float-to-Decimal conversion"""
        result = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=0.3,  # Tricky float
            projected_ground_price_usd_per_kg=0.7,  # Tricky float
            species="Test",
            vessel_id="WSP-020"
        )
        # 0.3 × 0.7 should be 0.21 (not 0.20999999...)
        assert result["check_key_usd"] == 0.21


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    def test_full_workflow_simulation(self):
        """Test complete workflow: calculation → enrichment → variance"""
        # Step 1: Calculate $CHECK KEY at-sea
        check_key = ProspectusCalculator.calculate_check_key(
            estimated_catch_kg=750.0,
            projected_ground_price_usd_per_kg=22.50,
            species="Bluefin Tuna",
            vessel_id="WSP-PREMIUM-001",
            metadata={
                "fishing_area": "FAO-77",
                "gear_type": "purse_seine",
                "quality_grade": "sushi_grade"
            }
        )
        
        assert check_key["check_key_usd"] == 16875.00  # 750 × 22.50
        
        # Step 2: Enrich with market data
        market_data = {
            "spot_price": 23.00,
            "avg_price_30d": 22.00,
            "variance": 4.5,
            "confidence": 0.95
        }
        enriched = ProspectusCalculator.enrich_with_market_data(check_key, market_data)
        
        assert enriched["market_enrichment"]["current_spot_price_usd"] == 23.00
        assert enriched["market_enrichment"]["spot_check_key_usd"] == 17250.00  # 750 × 23.00
        
        # Step 3: Calculate variance after landing
        actual_landed_value = 17100.00  # Slightly higher than projected
        variance = ProspectusCalculator.calculate_variance(check_key, actual_landed_value)
        
        assert variance["variance_usd"] == 225.00  # 17100 - 16875
        assert variance["variance_percent"] == 1.33  # (225 / 16875) * 100
        assert variance["accuracy_classification"] == "excellent"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
