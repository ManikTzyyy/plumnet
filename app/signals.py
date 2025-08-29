from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from .models import Server, IPPool, Paket, Client

# Kalau hapus Server → nullify relasi turunannya
@receiver(post_delete, sender=Server)
def nullify_related_on_server_delete(sender, instance, **kwargs):
    # Nullify IPPool
    IPPool.objects.filter(id_server=instance).update(id_server=None)
    # Nullify Paket yang ada di server ini
    Paket.objects.filter(id_ip_pool__id_server=None).update(id_ip_pool=None)
    # Nullify Client
    Client.objects.filter(id_paket__id_ip_pool=None).update(id_paket=None)
    Client.objects.filter(temp_paket__id_ip_pool=None).update(temp_paket=None)


# Kalau hapus IPPool → nullify Paket & Client
@receiver(pre_delete, sender=IPPool)
def nullify_related_on_ippool_delete(sender, instance, **kwargs):
    Paket.objects.filter(id_ip_pool=instance).update(id_ip_pool=None)
    Client.objects.filter(id_paket__id_ip_pool=instance).update(id_paket=None)
    Client.objects.filter(temp_paket__id_ip_pool=instance).update(temp_paket=None)


# Kalau hapus Paket → nullify Client
@receiver(pre_delete, sender=Paket)
def nullify_related_on_paket_delete(sender, instance, **kwargs):
    Client.objects.filter(id_paket=instance).update(id_paket=None)
    Client.objects.filter(temp_paket=instance).update(temp_paket=None)
