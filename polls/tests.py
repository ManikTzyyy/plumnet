from django.core.mail import send_mail

from polls.models import Client, IPPool, Paket

send_mail(
    subject="Tes Email Django",
    message="Halo, ini email percobaan dari Django.",
    from_email=None,  # otomatis pakai DEFAULT_FROM_EMAIL
    recipient_list=["manikyogantara@gmail.com"],
)


server=10


pool_data = list(IPPool.objects.filter(id_server=server).values_list('name', flat=True))
profile_data = list(Paket.objects.filter(id_ip_pool__id_server=server).values_list('name', flat=True))
client_data = list(Client.objects.filter(id_paket__id_ip_pool__id_server=server).values_list('pppoe', flat=True))


print(pool_data, profile_data, client_data)