"""
🔍 Prometheus Metrics for SeaTrace
For the Commons Good! 🌊
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

error_count = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

license_verifications = Counter(
    'license_verifications_total',
    'Total license verifications',
    ['result']  # 'valid', 'invalid', 'revoked'
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get endpoint path
        endpoint = request.url.path
        method = request.method
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            status = response.status_code
            
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Record error
            error_count.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            
            logger.error(f"Error processing request: {e}")
            raise

async def metrics_endpoint(request: Request):
    """Endpoint to expose Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def setup_metrics_endpoint(app):
    """Add /metrics endpoint to FastAPI app"""
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])
    app.add_middleware(MetricsMiddleware)
    logger.info("✅ Metrics endpoint configured: /metrics")
