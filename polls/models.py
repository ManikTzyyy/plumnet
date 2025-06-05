from django.db import models

from .utils.formatPrice import format_rupiah

class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255) 
    genieacs = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class IPPool(models.Model):
    id_server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='servers') 
    name = models.CharField(max_length=100)
    ip_range = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.id_server.name}"
    
class Paket(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    limit = models.CharField(max_length=255)
    id_ip_pool = models.ForeignKey(IPPool, on_delete=models.CASCADE, related_name='ip_pools')
    
    def __str__(self):
        return f"{format_rupiah(self.price)} - {self.name} - {self.limit} - {self.id_ip_pool.id_server.name}"
    
class Client(models.Model):
    id_paket = models.ForeignKey(Paket, on_delete=models.CASCADE, related_name='pakets') 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    pppoe = models.CharField(max_length=255) 
    password = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

