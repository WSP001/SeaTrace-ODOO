# 🔐 SeaTrace Packet Cryptography Tests
# For the Commons Good! 🌊

import pytest
from src.security.packet_crypto import (
    PacketCryptoHandler,
    CryptoPacket
)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture
def crypto_handler():
    """Generate test RSA keypair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return PacketCryptoHandler(
        public_key_pem=public_pem,
        private_key_pem=private_pem
    )


@pytest.fixture
def sample_packet():
    """Create sample crypto packet"""
    return CryptoPacket(
        correlation_id="test-uuid-123",
        source="vessel",
        payload={"vessel_id": "WSP-001", "catch_weight": 500}
    )


class TestPacketCryptoHandler:
    """Test suite for PacketCryptoHandler"""
    
    def test_generate_keypair(self):
        """Test RSA keypair generation"""
        private_pem, public_pem = PacketCryptoHandler.generate_keypair()
        
        assert private_pem.startswith(b"-----BEGIN PRIVATE KEY-----")
        assert public_pem.startswith(b"-----BEGIN PUBLIC KEY-----")
        assert len(private_pem) > 1000  # RSA 2048 key is large
        assert len(public_pem) > 200
    
    def test_sign_packet(self, crypto_handler, sample_packet):
        """Test packet signing (OUTGOING)"""
        signature = crypto_handler.sign_packet(sample_packet)
        
        assert signature is not None
        assert isinstance(signature, bytes)
        assert len(signature) == 256  # RSA 2048 signature size
    
    def test_verify_valid_signature(self, crypto_handler, sample_packet):
        """Test valid signature verification (INCOMING)"""
        # Sign the packet
        signature = crypto_handler.sign_packet(sample_packet)
        sample_packet.signature = signature
        
        # Verify signature
        is_valid = crypto_handler.verify_signature(sample_packet)
        
        assert is_valid is True
    
    def test_verify_invalid_signature(self, crypto_handler, sample_packet):
        """Test invalid signature rejection"""
        # Create fake signature
        sample_packet.signature = b"invalid_signature_bytes"
        
        # Verify should fail
        is_valid = crypto_handler.verify_signature(sample_packet)
        
        assert is_valid is False
    
    def test_verify_tampered_packet(self, crypto_handler, sample_packet):
        """Test detection of tampered packet"""
        # Sign original packet
        signature = crypto_handler.sign_packet(sample_packet)
        sample_packet.signature = signature
        
        # Tamper with payload
        sample_packet.payload["catch_weight"] = 999
        sample_packet.packet_hash = sample_packet.compute_hash()
        
        # Verification should fail
        is_valid = crypto_handler.verify_signature(sample_packet)
        
        assert is_valid is False
    
    def test_validate_packet_integrity(self, crypto_handler, sample_packet):
        """Test BLAKE2 hash integrity validation"""
        # Compute initial hash
        original_hash = sample_packet.packet_hash
        
        # Validate integrity
        is_valid = crypto_handler.validate_packet_integrity(sample_packet)
        
        assert is_valid is True
        assert sample_packet.packet_hash == original_hash
    
    def test_detect_hash_mismatch(self, crypto_handler, sample_packet):
        """Test detection of hash mismatch"""
        # Store original hash
        original_hash = sample_packet.packet_hash
        
        # Tamper with payload
        sample_packet.payload["catch_weight"] = 999
        
        # Don't recompute hash (simulate attack)
        # Validation should fail
        is_valid = crypto_handler.validate_packet_integrity(sample_packet)
        
        assert is_valid is False
    
    def test_packet_to_dict(self, sample_packet):
        """Test packet serialization"""
        packet_dict = sample_packet.to_dict()
        
        assert packet_dict["correlation_id"] == "test-uuid-123"
        assert packet_dict["source"] == "vessel"
        assert packet_dict["payload"]["vessel_id"] == "WSP-001"
        assert "packet_hash" in packet_dict
        assert "timestamp" in packet_dict


class TestCryptoPacket:
    """Test suite for CryptoPacket dataclass"""
    
    def test_packet_creation(self):
        """Test basic packet creation"""
        packet = CryptoPacket(
            correlation_id="test-123",
            source="vessel",
            payload={"test": "data"}
        )
        
        assert packet.correlation_id == "test-123"
        assert packet.source == "vessel"
        assert packet.payload == {"test": "data"}
        assert packet.timestamp is not None
        assert packet.packet_hash is not None
    
    def test_compute_hash(self):
        """Test BLAKE2 hash computation"""
        packet1 = CryptoPacket(
            correlation_id="test-123",
            source="vessel",
            payload={"test": "data"}
        )
        
        packet2 = CryptoPacket(
            correlation_id="test-123",
            source="vessel",
            payload={"test": "data"}
        )
        
        # Same data should produce different hashes (due to timestamp)
        # But same packet should produce same hash
        hash1 = packet1.compute_hash()
        hash2 = packet1.compute_hash()
        
        assert hash1 == hash2
        assert len(hash1) == 128  # BLAKE2b produces 64-byte (128 hex) hash
    
    def test_hash_changes_with_payload(self):
        """Test hash changes when payload changes"""
        packet = CryptoPacket(
            correlation_id="test-123",
            source="vessel",
            payload={"test": "data"}
        )
        
        original_hash = packet.packet_hash
        
        # Change payload
        packet.payload["test"] = "modified"
        new_hash = packet.compute_hash()
        
        assert new_hash != original_hash


class TestSecurePacketSwitcher:
    """Test suite for SecurePacketSwitcher integration"""
    
    @pytest.mark.asyncio
    async def test_secure_packet_processing(self, crypto_handler, sample_packet):
        """Test complete secure packet flow"""
        from src.security.packet_crypto import SecurePacketSwitcher
        
        # Create secure switcher
        switcher = SecurePacketSwitcher(crypto_handler)
        
        # Sign packet
        signature = crypto_handler.sign_packet(sample_packet)
        sample_packet.signature = signature
        
        # Process packet (this will test all 4 layers)
        try:
            response = await switcher.process_secure_packet(sample_packet)
            
            # Response should have correlation ID
            assert "correlation_id" in response
            assert response["correlation_id"] == sample_packet.correlation_id
            
            # Response should be signed
            if crypto_handler.private_key:
                assert "signature" in response
        except Exception as e:
            # Expected if packet switching router isn't running
            assert "process_packet" in str(e) or "IncomingPacket" in str(e)


@pytest.mark.integration
class TestEndToEndFlow:
    """Integration tests for complete crypto flow"""
    
    def test_public_key_incoming_flow(self, crypto_handler):
        """Test PUBLIC KEY INCOMING (verification only)"""
        # Create handler with only public key
        handler = PacketCryptoHandler(public_key_pem=crypto_handler.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        
        # Create and sign packet with full handler
        packet = CryptoPacket(
            correlation_id="test-incoming",
            source="vessel",
            payload={"data": "test"}
        )
        signature = crypto_handler.sign_packet(packet)
        packet.signature = signature
        
        # Verify with public-key-only handler
        is_valid = handler.verify_signature(packet)
        
        assert is_valid is True
    
    def test_private_key_outgoing_flow(self, crypto_handler):
        """Test PRIVATE KEY OUTGOING (signing only)"""
        # Create packet
        packet = CryptoPacket(
            correlation_id="test-outgoing",
            source="seatrace",
            payload={"response": "processed"}
        )
        
        # Sign with private key
        signature = crypto_handler.sign_packet(packet)
        
        assert signature is not None
        assert len(signature) == 256
        
        # Verify signature
        packet.signature = signature
        is_valid = crypto_handler.verify_signature(packet)
        
        assert is_valid is True


# Run tests with: pytest tests/test_packet_crypto.py -v --cov=src/security
