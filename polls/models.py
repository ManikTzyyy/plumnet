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
    id_server = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, blank=True, related_name='servers') 
    name = models.CharField(max_length=100)
    ip_range = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.id_server.name}"
    
class Paket(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    limit = models.CharField(max_length=255)
    id_ip_pool = models.ForeignKey(IPPool, on_delete=models.CASCADE,null=True, blank=True, related_name='ip_pools')
    
    def __str__(self):
        return f"{format_rupiah(self.price)} - {self.name} - {self.limit} - {self.id_ip_pool.id_server.name}"


class Client(models.Model):
    id_paket = models.ForeignKey(Paket, on_delete=models.CASCADE, null=True, blank=True, related_name='pakets') 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    pppoe = models.CharField(max_length=255) 
    password = models.CharField(max_length=255)
    isActive = models.BooleanField(default=False)
    isApproved = models.BooleanField(default=True)
    local_ip = models.GenericIPAddressField(blank=True, null=True)
    lat = models.CharField(max_length=255, null=True, blank=True)
    long = models.CharField(max_length=255, null=True, blank=True)
    temp_paket = models.ForeignKey(Paket, on_delete=models.CASCADE, related_name='temp_paket', null=True, blank=True)
    temp_name = models.CharField(max_length=255, null=True, blank=True)
    temp_address = models.CharField(max_length=255, null=True, blank=True)
    temp_phone = models.CharField(max_length=255, null=True, blank=True)
    temp_pppoe = models.CharField(max_length=255, null=True, blank=True)
    temp_password = models.CharField(max_length=255, null=True, blank=True)
    temp_local_ip = models.GenericIPAddressField(blank=True, null=True)
    temp_lat = models.CharField(max_length=255, null=True, blank=True)
    temp_long = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name



class Redaman(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='clients')
    value = models.CharField(max_length=255)
    create_at = models.DateTimeField()