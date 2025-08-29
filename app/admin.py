from django.contrib import admin
from .models import Server, IPPool, Paket, Client, Redaman

admin.site.register(Server)
admin.site.register(IPPool)
admin.site.register(Paket)
admin.site.register(Client)
admin.site.register(Redaman)
