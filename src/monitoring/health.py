"""
🔍 Health Check System
For the Commons Good! 🌊
"""

from typing import Dict, Callable, Awaitable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    """Manages health checks for various system components"""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Awaitable[bool]]] = {}
    
    def register_check(self, name: str, check_func: Callable[[], Awaitable[bool]]):
        """
        Register a health check
        
        Args:
            name: Name of the check (e.g., 'database', 'redis')
            check_func: Async function that returns True if healthy
        """
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def run_checks(self) -> Dict[str, any]:
        """
        Run all health checks
        
        Returns:
            Dictionary with check results
        """
        results = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'healthy',
            'checks': {}
        }
        
        for name, check_func in self.checks.items():
            try:
                is_healthy = await check_func()
                results['checks'][name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'healthy': is_healthy
                }
                
                if not is_healthy:
                    results['status'] = 'degraded'
                    logger.warning(f"Health check failed: {name}")
            
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'healthy': False,
                    'error': str(e)
                }
                results['status'] = 'unhealthy'
                logger.error(f"Health check error for {name}: {e}")
        
        return results

# Global health checker instance
health_checker = HealthChecker()

# Example health checks
async def check_api() -> bool:
    """Check if API is responding"""
    return True

async def check_database() -> bool:
    """Check database connection"""
    # TODO: Implement actual database check
    return True

async def check_redis() -> bool:
    """Check Redis connection"""
    # TODO: Implement actual Redis check
    return True

# Register default checks
health_checker.register_check('api', check_api)
health_checker.register_check('database', check_database)
health_checker.register_check('redis', check_redis)
