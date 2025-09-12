from django.db.models.signals import pre_delete, post_delete, pre_save, post_save
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




@receiver(post_save, sender=Client)
def update_used_ips_on_save(sender, instance, created, **kwargs):
    if created:
        if instance.id_paket:
            instance.id_paket.used_ips += 1
            instance.id_paket.save()
    else:
        # kasus update -> cek apakah paket berubah
        if instance.id_paket_id != instance._old_paket_id:
            # kurangi paket lama
            if instance._old_paket_id:
                old_paket = Paket.objects.filter(id=instance._old_paket_id).first()
                if old_paket:
                    old_paket.used_ips = max(0, old_paket.used_ips - 1)
                    old_paket.save()
            # tambah paket baru
            if instance.id_paket:
                instance.id_paket.used_ips += 1
                instance.id_paket.save()

@receiver(post_delete, sender=Client)
def update_used_ips_on_delete(sender, instance, **kwargs):
    if instance.id_paket:
        instance.id_paket.used_ips = max(0, instance.id_paket.used_ips - 1)
        instance.id_paket.save()



@receiver(pre_save, sender=Client)
def track_old_paket(sender, instance, **kwargs):
    if instance.pk:  # berarti sedang update, bukan create
        old_client = Client.objects.get(pk=instance.pk)
        instance._old_paket_id = old_client.id_paket_id
    else:
        instance._old_paket_id = None