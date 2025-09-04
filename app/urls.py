from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('map', views.map, name='map'),
    path('test', views.testPage, name='testPage'),

    #dashboard
    path('', views.dashboard, name='dashboard'),
    path('get-server-info/<int:server_id>/', views.get_server_info, name='get_server_info'),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


    path('server-list/', views.server, name='server'),
    path('paket-list/', views.paket, name='paket'),
    path('client/', views.client, name='client'),
    path('verifikasi/', views.verifikasi, name='verifikasi'),

    #forms
    path('add-server/', views.addServer, name='add-server'),
    path('add-paket/', views.addProfile, name='add-paket'),
    path('add-ip-pool/', views.addIp, name='add-ip'),
    path('add-client/', views.addClient, name='add-client'),

    #edit
    path('server/edit/<int:pk>/', views.edit_server, name='edit-server'),
    path('paket/edit/<int:pk>/', views.edit_paket, name='edit-paket'),
    path('ip/edit/<int:pk>/', views.edit_ip, name='edit-ip'),
    path('client/edit/<int:pk>/', views.edit_client, name='edit-client'),
    #delete
    path('server/<int:pk>/delete/', views.delete_server, name='delete-server'),
    path('paket/<int:pk>/delete/', views.delete_paket, name='delete-paket'),
    path('ip/<int:pk>/delete/', views.delete_ip, name='delete-ip'),
    path('client/<int:pk>/delete/', views.delete_client, name='delete-client'),

    #detailPages
    path('server/id=<int:server_id>/', views.detailServer, name='detail-server'),

    path('client/id=<int:client_id>', views.detailClient, name='detail-client'),

    #==========================
    path('client/<int:client_id>/toggle/', views.toggle_activasi, name='toggle_activasi'),
    path('client/<int:client_id>/payment/', views.toggle_pembayaran, name='toggle_pembayaran'),

    path('client/activasi/multi', views.activasi_multi_client, name="activasi_multi"),

    path('client/<int:client_id>/verification/', views.toggle_verif, name='toggle_verif'),
   
    path("test-conn/", views.test_conn_view, name="test_conn"),
    path("auto-conf/", views.auto_config, name="auto-conf"),


    path("client/reboot/", views.reboot, name="reboot"),

    path("api/", views.random_devices),

     path("api/client-remote/<int:client_id>/", views.get_client_remote, name="client-remote"),

    path("api/genieacs/<int:client_id>/", views.get_genieacs_data, name="get_genieacs_data"),



]


