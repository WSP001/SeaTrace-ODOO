"""
KeyRotationManager: Automated key rotation system for SeaTrace002 microservices.
"""
from datetime import timedelta
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from prometheus_client import Counter, Gauge
import structlog

logger = structlog.get_logger()

KEY_ROTATION_COUNT = Counter("key_rotation_count", "Total number of key rotations")
KEY_ROTATION_FAILURES = Counter("key_rotation_failures_total", "Total number of key rotation failures")
KEY_AGE = Gauge("key_age_days", "Age of current key in days", ["key_type"])

class KeyRotationManager:
    """Automated key rotation for all services"""
    def __init__(self, redis_client, mongodb_client):
        self.redis = redis_client
        self.mongodb = mongodb_client
        self.rotation_interval = timedelta(days=30)
        self.key_types = ["AIS", "GFW", "JWT", "IOT"]
        
    async def _generate_new_keypair(self, key_type: str):
        """Generate new RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            
            version = await self._get_next_version(key_type)
            await self._store_key_pair(key_type, version, private_key, public_key)
            
            KEY_ROTATION_COUNT.inc()
            KEY_AGE.labels(key_type=key_type).set(0)
            
            logger.info("Generated new key pair", 
                       key_type=key_type, 
                       version=version)
            
            return version
            
        except Exception as e:
            KEY_ROTATION_FAILURES.inc()
            logger.error("Failed to generate key pair",
                        key_type=key_type,
                        error=str(e))
            raise

    async def _store_key_pair(self, key_type: str, version: int, private_key, public_key):
        """Store the key pair securely"""
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        await self.mongodb.keys.insert_one({
            "key_type": key_type,
            "version": version,
            "private_key": private_pem.decode(),
            "public_key": public_pem.decode(),
            "created_at": datetime.utcnow()
        })

    async def _get_next_version(self, key_type: str):
        """Get next version number for key type"""
        return await self.redis.incr(f"{key_type}_version")

    async def rotate_service_keys(self, service_name: str):
        """Rotate all keys for a specific service"""
        for key_type in self.key_types:
            try:
                version = await self._generate_new_keypair(key_type)
                if await self._validate_key_rotation(key_type, version):
                    logger.info("Key rotation successful",
                              service=service_name,
                              key_type=key_type,
                              version=version)
                else:
                    await self._rollback_rotation(key_type, version)
            except Exception as e:
                logger.error("Key rotation failed",
                           service=service_name,
                           key_type=key_type,
                           error=str(e))
                raise

    async def _validate_key_rotation(self, key_type: str, version: str):
        """Validate newly rotated keys"""
        try:
            test_message = b"Key rotation validation test"
            new_private = await self._get_private_key(key_type, version)
            new_public = await self._get_public_key(key_type, version)
            
            # Test encryption/decryption
            encrypted = new_public.encrypt(test_message)
            decrypted = new_private.decrypt(encrypted)
            
            return decrypted == test_message
            
        except Exception as e:
            logger.error("Key validation failed",
                        key_type=key_type,
                        version=version,
                        error=str(e))
            return False

    async def _rollback_rotation(self, key_type: str, version: str):
        """Rollback failed key rotation"""
        try:
            await self.mongodb.keys.delete_one({
                "key_type": key_type,
                "version": version
            })
            await self.redis.decr(f"{key_type}_version")
            
            logger.info("Key rotation rolled back",
                       key_type=key_type,
                       version=version)
        except Exception as e:
            logger.error("Rollback failed",
                        key_type=key_type,
                        version=version,
                        error=str(e))
            raise
