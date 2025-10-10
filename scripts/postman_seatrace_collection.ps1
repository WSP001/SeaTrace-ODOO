#!/usr/bin/env pwsh
# SeaTrace Postman Collection Generator
# Aligned with Four Pillars: Autonomy, Accountability, Optimization, Collaboration

# Configuration
$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

# Log function with Four Pillars tagging
function Write-PillarLog {
    param (
        [string]$Message,
        [ValidateSet("Autonomy", "Accountability", "Optimization", "Collaboration", "Info", "Warning", "Error")]
        [string]$Pillar = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Pillar) {
        "Autonomy" { "Cyan" }
        "Accountability" { "Green" }
        "Optimization" { "Yellow" }
        "Collaboration" { "Magenta" }
        "Info" { "White" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$Pillar] $Message" -ForegroundColor $color
}

Write-Host "SeaTrace Postman Collection Generator" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

# Create directory for Postman collections
$projectRoot = Split-Path -Parent $PSScriptRoot
$postmanDir = Join-Path $projectRoot "postman"
if (-not (Test-Path $postmanDir)) {
    New-Item -Path $postmanDir -ItemType Directory -Force | Out-Null
    Write-PillarLog "Created Postman directory: $postmanDir" -Pillar "Autonomy"
}

# Create SeaTrace Postman collection
$seaTraceCollection = @{
    info = @{
        name = "SeaTrace API Collection"
        description = "API collection for the SeaTrace system following the Four Pillars architecture"
        schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    }
    item = @(
        # SeaSide (HOLD) API Endpoints
        @{
            name = "SeaSide (HOLD)"
            description = "Vessel tracking and initial data capture"
            item = @(
                @{
                    name = "Get Vessel Data"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/seaside/vessels"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "seaside", "vessels")
                        }
                    }
                },
                @{
                    name = "Get Vessel by ID"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/seaside/vessels/{{vessel_id}}"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "seaside", "vessels", "{{vessel_id}}")
                        }
                    }
                },
                @{
                    name = "Submit Vessel Position"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "vessel_id": "{{vessel_id}}",
    "timestamp": "{{$isoTimestamp}}",
    "latitude": 42.3601,
    "longitude": -71.0589,
    "speed": 5.2,
    "course": 180.5,
    "source": "AIS"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/seaside/vessels/{{vessel_id}}/positions"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "seaside", "vessels", "{{vessel_id}}", "positions")
                        }
                    }
                },
                @{
                    name = "Generate Quality Score"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "vessel_id": "{{vessel_id}}",
    "fishing_area": "FAO-27",
    "species_code": "COD",
    "gear_type": "Trawl"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/seaside/quality/score"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "seaside", "quality", "score")
                        }
                    }
                }
            )
        },
        # DeckSide (RECORD) API Endpoints
        @{
            name = "DeckSide (RECORD)"
            description = "Catch verification and certification"
            item = @(
                @{
                    name = "Get Catch Data"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/deckside/catches"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "deckside", "catches")
                        }
                    }
                },
                @{
                    name = "Get Catch by ID"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/deckside/catches/{{catch_id}}"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "deckside", "catches", "{{catch_id}}")
                        }
                    }
                },
                @{
                    name = "Submit Catch Data"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "vessel_id": "{{vessel_id}}",
    "catch_id": "{{$guid}}",
    "trip_id": "TRIP-001",
    "gear_type": "Trawl",
    "fishing_area": "FAO-27",
    "fishing_method": "Bottom trawling",
    "items": [
        {
            "species_code": "COD",
            "scientific_name": "Gadus morhua",
            "common_name": "Atlantic cod",
            "weight_kg": 450.5,
            "count": 200,
            "size_range": "40-60cm",
            "is_target_species": true
        }
    ],
    "total_weight_kg": 450.5,
    "observer_present": true,
    "observer_name": "John Smith"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/deckside/catches"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "deckside", "catches")
                        }
                    }
                },
                @{
                    name = "Generate QR Code"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "catch_id": "{{catch_id}}",
    "vessel_id": "{{vessel_id}}",
    "product_id": "{{$guid}}"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/deckside/qrcode"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "deckside", "qrcode")
                        }
                    }
                }
            )
        },
        # DockSide (STORE) API Endpoints
        @{
            name = "DockSide (STORE)"
            description = "Supply chain and storage management"
            item = @(
                @{
                    name = "Get Processing Data"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/dockside/processing"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "dockside", "processing")
                        }
                    }
                },
                @{
                    name = "Get Processing by ID"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/dockside/processing/{{processing_id}}"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "dockside", "processing", "{{processing_id}}")
                        }
                    }
                },
                @{
                    name = "Submit Processing Data"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "processing_id": "{{$guid}}",
    "catch_id": "{{catch_id}}",
    "facility_name": "Coastal Processing Plant",
    "facility_id": "FACILITY-001",
    "processing_method": "Filleting",
    "batch_number": "BATCH-001",
    "lot_number": "LOT-001",
    "products": [
        {
            "product_id": "{{$guid}}",
            "description": "Atlantic cod fillets",
            "product_form": "Fillet",
            "weight_kg": 300.2,
            "packaging_type": "Vacuum sealed",
            "production_date": "{{$isoTimestamp}}"
        }
    ],
    "temperature_logs": [
        {
            "timestamp": "{{$isoTimestamp}}",
            "temperature_celsius": 2.1,
            "location": "Processing room",
            "sensor_id": "SENSOR-001"
        }
    ]
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/dockside/processing"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "dockside", "processing")
                        }
                    }
                },
                @{
                    name = "Store BONE File"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "file_id": "{{$guid}}",
    "file_name": "quality_certificate.pdf",
    "mime_type": "application/pdf",
    "processing_id": "{{processing_id}}",
    "file_content": "base64encodedcontent"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/dockside/bone/files"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "dockside", "bone", "files")
                        }
                    }
                }
            )
        },
        # MarketSide (EXCHANGE) API Endpoints
        @{
            name = "MarketSide (EXCHANGE)"
            description = "Trading platform and consumer interface"
            item = @(
                @{
                    name = "Get Market Data"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/marketside/transactions"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "marketside", "transactions")
                        }
                    }
                },
                @{
                    name = "Get Transaction by ID"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/marketside/transactions/{{transaction_id}}"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "marketside", "transactions", "{{transaction_id}}")
                        }
                    }
                },
                @{
                    name = "Submit Transaction"
                    request = @{
                        method = "POST"
                        header = @(
                            @{
                                key = "Content-Type"
                                value = "application/json"
                            }
                        )
                        body = @{
                            mode = "raw"
                            raw = @"
{
    "transaction_id": "{{$guid}}",
    "product_id": "{{product_id}}",
    "seller_id": "SELLER-001",
    "buyer_id": "BUYER-001",
    "price_per_unit": 12.50,
    "currency": "USD",
    "total_value": 3750.0,
    "payment_method": "Bank transfer",
    "market_location": "Boston Fish Market",
    "transaction_type": "Direct sale"
}
"@
                        }
                        url = @{
                            raw = "{{base_url}}/api/v1/marketside/transactions"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "marketside", "transactions")
                        }
                    }
                },
                @{
                    name = "Verify Product"
                    request = @{
                        method = "GET"
                        header = @()
                        url = @{
                            raw = "{{base_url}}/api/v1/marketside/verify/{{product_id}}"
                            host = @("{{base_url}}")
                            path = @("api", "v1", "marketside", "verify", "{{product_id}}")
                        }
                    }
                }
            )
        }
    )
}

# Create environments
$environments = @(
    @{
        name = "Local Development"
        values = @(
            @{
                key = "base_url"
                value = "http://localhost:8080"
                enabled = $true
            },
            @{
                key = "vessel_id"
                value = "VESSEL-001"
                enabled = $true
            },
            @{
                key = "catch_id"
                value = "CATCH-001"
                enabled = $true
            },
            @{
                key = "processing_id"
                value = "PROC-001"
                enabled = $true
            },
            @{
                key = "product_id"
                value = "PROD-001"
                enabled = $true
            },
            @{
                key = "transaction_id"
                value = "TRANS-001"
                enabled = $true
            }
        )
    },
    @{
        name = "Kubernetes Development"
        values = @(
            @{
                key = "base_url"
                value = "http://seatrace.kubernetes.docker.internal"
                enabled = $true
            },
            @{
                key = "vessel_id"
                value = "VESSEL-001"
                enabled = $true
            },
            @{
                key = "catch_id"
                value = "CATCH-001"
                enabled = $true
            },
            @{
                key = "processing_id"
                value = "PROC-001"
                enabled = $true
            },
            @{
                key = "product_id"
                value = "PROD-001"
                enabled = $true
            },
            @{
                key = "transaction_id"
                value = "TRANS-001"
                enabled = $true
            }
        )
    },
    @{
        name = "Production"
        values = @(
            @{
                key = "base_url"
                value = "https://api.seatrace.worldseafoodproducers.com"
                enabled = $true
            },
            @{
                key = "vessel_id"
                value = "VESSEL-001"
                enabled = $true
            },
            @{
                key = "catch_id"
                value = "CATCH-001"
                enabled = $true
            },
            @{
                key = "processing_id"
                value = "PROC-001"
                enabled = $true
            },
            @{
                key = "product_id"
                value = "PROD-001"
                enabled = $true
            },
            @{
                key = "transaction_id"
                value = "TRANS-001"
                enabled = $true
            }
        )
    }
)

# Save collection to file
$collectionPath = Join-Path $postmanDir "SeaTrace_Collection.json"
$seaTraceCollection | ConvertTo-Json -Depth 10 | Set-Content -Path $collectionPath
Write-PillarLog "Created Postman collection: $collectionPath" -Pillar "Autonomy"

# Save environments to files
foreach ($env in $environments) {
    $envPath = Join-Path $postmanDir "$($env.name.Replace(' ', '_'))_Environment.json"
    $env | ConvertTo-Json -Depth 10 | Set-Content -Path $envPath
    Write-PillarLog "Created Postman environment: $envPath" -Pillar "Accountability"
}

# Create README for Postman collection
$postmanReadme = @"
# SeaTrace Postman Collection

This directory contains Postman collections and environments for testing the SeaTrace API.

## Collection

The SeaTrace API Collection includes endpoints for all Four Pillars:

1. **SeaSide (HOLD)**: Vessel tracking and initial data capture
2. **DeckSide (RECORD)**: Catch verification and certification
3. **Dockside (STORE)**: Supply chain and storage management
4. **MarketSide (EXCHANGE)**: Trading platform and consumer interface

## Environments

Three environments are provided:

1. **Local Development**: For testing against a local development environment
2. **Kubernetes Development**: For testing against a Kubernetes development environment
3. **Production**: For testing against the production environment

## Usage

1. Import the collection and environments into Postman
2. Select the appropriate environment
3. Run the requests individually or as a collection

## Automation

The collection can be run using Newman, Postman's command-line collection runner:

```bash
newman run SeaTrace_Collection.json -e Local_Development_Environment.json
```

## Integration with CI/CD

Add the following to your CI/CD pipeline:

```yaml
- name: Run API Tests
  run: |
    npm install -g newman
    newman run ./postman/SeaTrace_Collection.json -e ./postman/Kubernetes_Development_Environment.json
```
"@

$postmanReadmePath = Join-Path $postmanDir "README.md"
Set-Content -Path $postmanReadmePath -Value $postmanReadme
Write-PillarLog "Created README for Postman collection" -Pillar "Collaboration"

Write-PillarLog "Postman collection generation completed successfully!" -Pillar "Info"
Write-PillarLog "The Postman collection is available at: $collectionPath" -Pillar "Info"
Write-PillarLog "Import the collection and environments into Postman to test the SeaTrace API" -Pillar "Info"
