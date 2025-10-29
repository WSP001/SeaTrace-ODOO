"""Business logic for DeckSide service (RECORD layer)"""
import structlog
from datetime import datetime
from typing import Dict, Tuple
from .models import VesselData, ValidationResult, ValidationError

logger = structlog.get_logger()

class DeckSideProcessor:
    """Processes and validates vessel records"""
    
    # Business rules
    MIN_CATCH_WEIGHT = 0.1  # kg
    MAX_CATCH_WEIGHT = 1000000  # kg
    VALID_SPECIES = {
        "Tuna", "Salmon", "Cod", "Herring", "Pollock",
        "Mackerel", "Sardine", "Anchovy", "Haddock"
    }
    
    @staticmethod
    def validate_vessel_data(vessel_data: VesselData) -> Tuple[ValidationResult, Dict]:
        """
        Validate vessel data against business rules.
        
        Returns:
            Tuple of (ValidationResult, enriched_data_dict)
        """
        errors = []
        warnings = []
        enriched_data = vessel_data.dict()
        
        # Validate catch weight
        if vessel_data.catch_weight < DeckSideProcessor.MIN_CATCH_WEIGHT:
            errors.append(ValidationError(
                field="catch_weight",
                message=f"Catch weight below minimum ({DeckSideProcessor.MIN_CATCH_WEIGHT} kg)",
                code="WEIGHT_TOO_LOW"
            ))
        
        if vessel_data.catch_weight > DeckSideProcessor.MAX_CATCH_WEIGHT:
            errors.append(ValidationError(
                field="catch_weight",
                message=f"Catch weight exceeds maximum ({DeckSideProcessor.MAX_CATCH_WEIGHT} kg)",
                code="WEIGHT_TOO_HIGH"
            ))
        
        # Warn if catch is unusually large (but still valid)
        if vessel_data.catch_weight > 500000:
            warnings.append("Unusually large catch detected - verify with vessel operator")
        
        # Validate species
        if vessel_data.species not in DeckSideProcessor.VALID_SPECIES:
            errors.append(ValidationError(
                field="species",
                message=f"Species '{vessel_data.species}' not in approved list",
                code="INVALID_SPECIES"
            ))
        
        # Validate vessel ID format
        if not vessel_data.vessel_id.startswith("WSP-"):
            warnings.append(f"Vessel ID '{vessel_data.vessel_id}' does not match WSP- prefix convention")
        
        # Validate location if provided
        if vessel_data.location:
            if vessel_data.location.latitude == 0 and vessel_data.location.longitude == 0:
                warnings.append("Location is at (0,0) - verify GPS data")
        else:
            warnings.append("No location data provided - enrichment limited")
        
        # Enrich data
        enriched_data["validated_at"] = datetime.utcnow().isoformat()
        enriched_data["validation_passed"] = len(errors) == 0
        enriched_data["enrichment_level"] = "basic"
        
        validation_result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
        logger.info(
            "vessel_validation_complete",
            vessel_id=vessel_data.vessel_id,
            valid=validation_result.valid,
            error_count=len(errors),
            warning_count=len(warnings)
        )
        
        return validation_result, enriched_data
    
    @staticmethod
    def enrich_vessel_data(vessel_data: VesselData, validation_result: ValidationResult) -> Dict:
        """
        Enrich vessel data with additional context.
        """
        enriched = vessel_data.dict()
        
        if validation_result.valid:
            # Add enrichment context
            enriched["enrichment"] = {
                "validated": True,
                "enriched_at": datetime.utcnow().isoformat(),
                "enrichment_rules_applied": ["weight_validation", "species_validation", "location_check"],
                "next_destination": "dockside"
            }
        
        return enriched
