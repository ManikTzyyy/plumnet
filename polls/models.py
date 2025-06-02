from django.db import models

# Create your models here.


#server

class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255) 
    genieacs = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class IPPool(models.Model):
    name = models.CharField(max_length=100)
    ip_range = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Paket(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    limit = models.CharField(max_length=255)
    ip_pool = models.ForeignKey(IPPool, on_delete=models.CASCADE, related_name='paket_list')
    
    def __str__(self):
        return self.name
    
class Client(models.Model):
    id_server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='server_list') 
    id_paket = models.ForeignKey(Paket, on_delete=models.CASCADE, related_name='paket_list') 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    pppoe = models.CharField(max_length=255) 
    password = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    

    def __str__(self):
        return self.name

