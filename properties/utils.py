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
    Returns detailed Redis cache metrics including memory usage.
    """
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        # Calculate hit ratio
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        hit_ratio = (hits / total) if total > 0 else 0.0
        
        # Get memory stats
        memory_stats = {
            'used_memory': info.get('used_memory', 0),
            'maxmemory': info.get('maxmemory', 0),
            'memory_usage_percentage': (
                (info['used_memory'] / info['maxmemory']) * 100 
                if info.get('maxmemory', 0) > 0 
                else 0
            )
        }
        
        metrics = {
            "hits": hits,
            "misses": misses,
            "hit_ratio": round(hit_ratio, 4),
            "memory": memory_stats,
            "keys": redis_conn.dbsize(),
            "uptime": info.get('uptime_in_seconds', 0)
        }
        
        logger.info(f"Redis Metrics: {json.dumps(metrics, indent=2)}")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get Redis metrics: {str(e)}")
        return {
            "error": str(e),
            "hits": 0,
            "misses": 0,
            "hit_ratio": 0.0
        }
