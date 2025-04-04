from django.urls import path
from . import views

urlpatterns = [
    #dashboard
    path('', views.dashboard, name='dashboard'),
    path('server-list/', views.server, name='server'),
    path('paket-list/', views.paket, name='paket'),
    path('client/', views.client, name='client'),
    path('verifikasi/', views.verifikasi, name='verifikasi'),
    path('setting/', views.setting, name='setting'),
    path('informasi/', views.informasi, name='informasi'),

    #forms
    path('add-server/', views.addServer, name='add-server'),
    path('add-paket/', views.addProfile, name='add-paket'),
    path('add-client/', views.addClient, name='add-client'),

    #detailPages
    path('server-list/detail/id=<int:server_id>/', views.detailServer, name='detail-server'),

    path('client/detail-client/', views.detailClient, name='detail-client'),

    
]
