from django.core.cache import cache
from .models import Property

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
