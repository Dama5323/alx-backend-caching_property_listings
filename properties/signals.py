from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

@receiver(post_save, sender=Property)
def invalidate_cache_on_save(sender, instance, **kwargs):
    cache.delete('all_properties')
    print("Cache cleared after save.")

@receiver(post_delete, sender=Property)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    cache.delete('all_properties')
    print("Cache cleared after delete.")
