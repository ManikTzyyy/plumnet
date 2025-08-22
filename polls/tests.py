from .models import Client, Paket, IPPool, Server

c = Client.objects.get(pk=10)
print("Client Paket:", c.id_paket, "IPPool:", c.id_paket.id_ip_pool, "Server:", c.id_paket.id_ip_pool.id_server)

new_paket = Paket.objects.get(pk=4)
print("New Paket:", new_paket, "IPPool:", new_paket.id_ip_pool, "Server:", new_paket.id_ip_pool.id_server)
