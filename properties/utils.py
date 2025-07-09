from django.core.cache import cache
from .models import Property
import logging
from django_redis import get_redis_connection
from django.core.serializers import serialize
import json

logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Fetches properties with Redis caching layer.
    Returns list of property dicts with optimized caching.
    """
    cache_key = 'all_properties_v2'  # Versioned key for cache invalidation
    
    # Try cache first
    properties = cache.get(cache_key)
    
    if properties is None:
        logger.info("Cache miss — fetching from DB and caching")
        try:
            properties = list(Property.objects.all().values(
                'id', 'title', 'description', 'price', 'location', 'created_at'
            ))
            # Cache with timeout and compression (django-redis specific)
            cache.set(cache_key, properties, timeout=3600, version=1, compress=True)
        except Exception as e:
            logger.error(f"Failed to fetch properties: {str(e)}")
            properties = []  # Fail gracefully
    else:
        logger.debug("Cache hit — using cached properties")
        
    return properties

def get_redis_cache_metrics():
    """
    Returns detailed Redis cache metrics with safe division for hit_ratio
    """
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total_requests = hits + misses
        
        # Safely calculate hit ratio (critical fix)
        hit_ratio = (hits / total_requests) if total_requests > 0 else 0.0
        
        metrics = {
            "hits": hits,
            "misses": misses,
            "total_requests": total_requests,
            "hit_ratio": round(hit_ratio, 4),  # Rounded to 4 decimal places
            "calculation_note": "safe division with total_requests check"
        }
        
        logger.info(f"Cache Metrics: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return {
            "error": str(e),
            "hits": 0,
            "misses": 0,
            "hit_ratio": 0.0,
            "emergency_fallback": True
        }
