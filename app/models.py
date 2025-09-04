from django.db import models

from .utils.utlis import format_rupiah


    


class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255) 
    genieacs = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, null=True, blank=True)
    long = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Gateway(models.Model):
    name= models.CharField(max_length=255, null=True, blank=True)
    server =  models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True, related_name='gateways') 
    lat = models.CharField(max_length=255, null=True, blank=True)
    long = models.CharField(max_length=255, null=True, blank=True)
    parent_lat = models.CharField(max_length=255, null=True, blank=True)
    parent_long = models.CharField(max_length=255, null=True, blank=True)
    

class IPPool(models.Model):
    id_server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True, related_name='servers') 
    name = models.CharField(max_length=100)
    ip_range = models.CharField(max_length=100)

    def __str__(self):
        server_name = self.id_server.name if self.id_server else "No Server"
        return f"{server_name} | {self.name} ({self.ip_range})"
    
class Paket(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    limit = models.CharField(max_length=255)
    id_ip_pool = models.ForeignKey(IPPool, on_delete=models.SET_NULL,null=True, blank=True, related_name='ip_pools')
       
    def __str__(self):
        server_name = self.id_ip_pool.id_server.name if self.id_ip_pool and self.id_ip_pool.id_server else "No Server"
        pool_name = self.id_ip_pool.name if self.id_ip_pool else "No IP Pool"
        range = self.id_ip_pool.ip_range if self.id_ip_pool else "No Range"
        return f"{format_rupiah(self.price)} | {self.limit} | {server_name}. ({range})"


class Client(models.Model):
    id_paket = models.ForeignKey(Paket, on_delete=models.SET_NULL, null=True, blank=True, related_name='pakets') 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255)
    pppoe = models.CharField(max_length=255) 
    password = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    isApproved = models.BooleanField(default=True)
    local_ip = models.GenericIPAddressField(blank=True, null=True)
    lat = models.CharField(max_length=255, null=True, blank=True)
    long = models.CharField(max_length=255, null=True, blank=True)
    temp_paket = models.ForeignKey(Paket, on_delete=models.SET_NULL, related_name='temp_paket', null=True, blank=True)
    temp_name = models.CharField(max_length=255, null=True, blank=True)
    temp_address = models.CharField(max_length=255, null=True, blank=True)
    temp_phone = models.CharField(max_length=255, null=True, blank=True)
    temp_email = models.EmailField(null=True, blank=True)
    temp_pppoe = models.CharField(max_length=255, null=True, blank=True)
    temp_password = models.CharField(max_length=255, null=True, blank=True)
    temp_local_ip = models.GenericIPAddressField(blank=True, null=True)
    temp_lat = models.CharField(max_length=255, null=True, blank=True)
    temp_long = models.CharField(max_length=255, null=True, blank=True)
    isServerNull = models.BooleanField(default=False)
    isPayed = models.BooleanField(default=True)
    lastPayment = models.DateField(null=True, blank=True)
    gateway = models.ForeignKey(Gateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='gateways') 
    temp_gateway = models.ForeignKey(Gateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='temp_gateways') 
    
    def __str__(self):
        client_name = self.name if self.name else "Unnamed Client"
        paket_name = self.id_paket.name if self.id_paket else "No Paket"
        return f"{client_name} ({paket_name})"



class Redaman(models.Model):
    id_client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients'
    )
    value = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
  
