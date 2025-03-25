from django.urls import path
from . import views

urlpatterns = [
    #dashboard
    path('', views.dashboard, name='dashboard'),
    path('server/', views.server, name='server'),
    path('paket/', views.paket, name='paket'),
    path('client/', views.client, name='client'),
    path('verifikasi/', views.verifikasi, name='verifikasi'),
    path('setting/', views.setting, name='setting'),
    path('informasi/', views.informasi, name='informasi'),
   
]