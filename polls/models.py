from django.db import models

# Create your models here.


#server

class Server(models.Model):
    name = models.CharField(max_length=255)
    host = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Simpan password terenkripsi jika diperlukan
    genieacs = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Paket(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    limit = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name