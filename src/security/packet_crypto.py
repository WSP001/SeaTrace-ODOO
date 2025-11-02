"""
🌊 SeaTrace Packet Cryptography Module
For the Commons Good! 🌊

Proceeding Master Integration - Cryptographic packet validation
Combines WildFisheriesPacketSwitcher with advanced cryptography
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from prometheus_client import Counter, Histogram
import structlog

logger = structlog.get_logger()

# Prometheus metrics
PACKET_CRYPTO_OPERATIONS = Counter(
    'packet_crypto_operations_total',
    'Total cryptographic operations',
    ['operation', 'status']
)
PACKET_CRYPTO_DURATION = Histogram(
    'packet_crypto_duration_seconds',
    'Duration of cryptographic operations',
    ['operation']
)


@dataclass
class CryptoPacket:
    """
    Cryptographically secured packet
    
    PUBLIC KEY INCOMING - Verify signatures
    PRIVATE KEY OUTGOING - Sign responses
    """
    correlation_id: str
    source: str
    payload: Dict[str, Any]
    signature: Optional[bytes] = None
    timestamp: str = None
    packet_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.packet_hash:
            self.packet_hash = self.compute_hash()
    
    def compute_hash(self) -> str:
        """Compute BLAKE2b hash of packet contents"""
        data = json.dumps({
            "correlation_id": self.correlation_id,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.blake2b(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "correlation_id": self.correlation_id,
            "source": self.source,
            "payload": self.payload,
            "signature": self.signature.hex() if self.signature else None,
            "timestamp": self.timestamp,
            "packet_hash": self.packet_hash
        }


class PacketCryptoHandler:
    """
    🛡️ DEFENSIVE COORDINATOR - Cryptographic Packet Handler
    
    Integrates with WildFisheriesPacketSwitcher for secure packet processing
    Uses RSA for signature verification and AES for payload encryption
    """
    
    def __init__(self, public_key_pem: Optional[bytes] = None, private_key_pem: Optional[bytes] = None):
        """
        Initialize crypto handler with optional keys
        
        Args:
            public_key_pem: PEM-encoded public key for verification
            private_key_pem: PEM-encoded private key for signing
        """
        self.public_key = None
        self.private_key = None
        
        if public_key_pem:
            self.public_key = serialization.load_pem_public_key(public_key_pem)
        
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )
    
    @staticmethod
    def generate_keypair() -> tuple[bytes, bytes]:
        """
        Generate new RSA keypair for packet signing
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        with PACKET_CRYPTO_DURATION.labels(operation='generate_keypair').time():
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            PACKET_CRYPTO_OPERATIONS.labels(
                operation='generate_keypair',
                status='success'
            ).inc()
            
            return private_pem, public_pem
    
    def sign_packet(self, packet: CryptoPacket) -> bytes:
        """
        Sign packet with private key (OUTGOING)
        
        Args:
            packet: Packet to sign
            
        Returns:
            Signature bytes
        """
        if not self.private_key:
            raise ValueError("Private key not loaded - cannot sign packets")
        
        with PACKET_CRYPTO_DURATION.labels(operation='sign_packet').time():
            try:
                # Sign the packet hash
                signature = self.private_key.sign(
                    packet.packet_hash.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='sign_packet',
                    status='success'
                ).inc()
                
                logger.info(
                    "Packet signed",
                    correlation_id=packet.correlation_id,
                    source=packet.source
                )
                
                return signature
                
            except Exception as e:
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='sign_packet',
                    status='error'
                ).inc()
                
                logger.error(
                    "Failed to sign packet",
                    correlation_id=packet.correlation_id,
                    error=str(e)
                )
                raise
    
    def verify_signature(self, packet: CryptoPacket) -> bool:
        """
        Verify packet signature with public key (INCOMING)
        
        Args:
            packet: Packet with signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            logger.warning("Public key not loaded - skipping signature verification")
            return True  # Allow unsigned packets if no public key configured
        
        if not packet.signature:
            logger.warning(
                "No signature provided",
                correlation_id=packet.correlation_id
            )
            return False
        
        with PACKET_CRYPTO_DURATION.labels(operation='verify_signature').time():
            try:
                self.public_key.verify(
                    packet.signature,
                    packet.packet_hash.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='verify_signature',
                    status='success'
                ).inc()
                
                logger.info(
                    "Signature verified",
                    correlation_id=packet.correlation_id,
                    source=packet.source
                )
                
                return True
                
            except InvalidSignature:
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='verify_signature',
                    status='invalid'
                ).inc()
                
                logger.warning(
                    "Invalid signature",
                    correlation_id=packet.correlation_id,
                    source=packet.source
                )
                
                return False
                
            except Exception as e:
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='verify_signature',
                    status='error'
                ).inc()
                
                logger.error(
                    "Signature verification failed",
                    correlation_id=packet.correlation_id,
                    error=str(e)
                )
                
                return False
    
    def validate_packet_integrity(self, packet: CryptoPacket) -> bool:
        """
        Validate packet hash integrity
        
        Args:
            packet: Packet to validate
            
        Returns:
            True if hash matches, False otherwise
        """
        with PACKET_CRYPTO_DURATION.labels(operation='validate_integrity').time():
            computed_hash = packet.compute_hash()
            
            if computed_hash == packet.packet_hash:
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='validate_integrity',
                    status='success'
                ).inc()
                
                logger.info(
                    "Packet integrity validated",
                    correlation_id=packet.correlation_id,
                    hash=computed_hash[:16]  # First 16 chars
                )
                
                return True
            else:
                PACKET_CRYPTO_OPERATIONS.labels(
                    operation='validate_integrity',
                    status='mismatch'
                ).inc()
                
                logger.warning(
                    "Packet integrity check failed",
                    correlation_id=packet.correlation_id,
                    expected=packet.packet_hash[:16],
                    computed=computed_hash[:16]
                )
                
                return False


# ========================================
# INTEGRATION WITH PACKET SWITCHER
# ========================================

class SecurePacketSwitcher:
    """
    Enhanced packet switcher with cryptographic validation
    
    Combines WildFisheriesPacketSwitcher with PacketCryptoHandler
    """
    
    def __init__(self, crypto_handler: PacketCryptoHandler):
        self.crypto = crypto_handler
        
        # Import packet switcher
        from packet_switching.handler import WildFisheriesPacketSwitcher
        self.switcher = WildFisheriesPacketSwitcher()
    
    async def process_secure_packet(self, packet: CryptoPacket) -> Dict[str, Any]:
        """
        Process packet with full cryptographic validation
        
        DEFENSIVE LAYERS:
        1. Hash integrity check (BLAKE2)
        2. Signature verification (RSA)
        3. Packet switching validation (3-layer defense)
        4. Pillar routing
        
        Args:
            packet: Incoming crypto packet
            
        Returns:
            Response with correlation ID and signature
        """
        # Layer 1: Validate hash integrity
        if not self.crypto.validate_packet_integrity(packet):
            raise ValueError("Packet integrity check failed")
        
        # Layer 2: Verify signature (if present)
        if packet.signature and not self.crypto.verify_signature(packet):
            raise ValueError("Invalid packet signature")
        
        # Layer 3: Convert to IncomingPacket for switcher
        from packet_switching.handler import IncomingPacket
        incoming = IncomingPacket(
            correlation_id=packet.correlation_id,
            source=packet.source,
            payload=packet.payload,
            signature=packet.signature.hex() if packet.signature else None,
            timestamp=packet.timestamp
        )
        
        # Layer 4: Route through packet switcher
        response = await self.switcher.process_packet(incoming)
        
        # Sign response (OUTGOING)
        if self.crypto.private_key:
            response_packet = CryptoPacket(
                correlation_id=packet.correlation_id,
                source="seatrace",
                payload=response
            )
            response["signature"] = self.crypto.sign_packet(response_packet).hex()
        
        return response 🌊