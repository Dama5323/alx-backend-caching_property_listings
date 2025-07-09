from django.core.cache import cache
from .models import Property
from django_redis import get_redis_connection

def get_all_properties():
    properties = cache.get('all_properties')

    if properties is None:
        print("Cache miss — fetching from DB.")
        properties = list(Property.objects.all().values(
            'id', 'title', 'description', 'price', 'location', 'created_at'
        ))
        cache.set('all_properties', properties, 3600)
    else:
        print("Cache hit — using cached data.")

    return properties

def get_redis_cache_metrics():
    redis_conn = get_redis_connection("default")
    info = redis_conn.info()

    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)

    total = hits + misses
    hit_ratio = (hits / total) if total > 0 else 0.0

    metrics = {
        "keyspace_hits": hits,
        "keyspace_misses": misses,
        "hit_ratio": round(hit_ratio, 4)
    }

    print("🔍 Redis Cache Metrics:", metrics)
    return metrics
