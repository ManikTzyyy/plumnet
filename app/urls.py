from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('map', views.map, name='map'),

    #dashboard
    path('', views.dashboard, name='dashboard'),
    path('get-server-info/<int:server_id>/', views.get_server_info, name='get_server_info'),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


    path('server-list/', views.server, name='server'),
    path('paket-list/', views.paket, name='paket'),
    path('client/', views.client, name='client'),
    path('activasi/', views.activasi, name='activasi'),

    #forms
    path('add-server/', views.addServer, name='add-server'),
    path('server/<int:server_id>/add-gateway/', views.addGateway, name='add-gateway'),
    path('add-paket/', views.addProfile, name='add-paket'),
    path('add-ip-pool/', views.addIp, name='add-ip'),
    path('add-client/', views.addClient, name='add-client'),

    #edit
    path('server/edit/<int:pk>/', views.edit_server, name='edit-server'),
    path('server/<int:server_id>/gateway/edit/<int:pk>/', views.edit_gateway, name='edit-gateway'),
    path('paket/edit/<int:pk>/', views.edit_paket, name='edit-paket'),
    path('ip/edit/<int:pk>/', views.edit_ip, name='edit-ip'),
    path('client/edit/<int:pk>/', views.edit_client, name='edit-client'),
    #delete
    path('server/<int:pk>/delete/', views.delete_server, name='delete-server'),
    path('gateway/<int:pk>/delete/', views.delete_gateway, name='delete-gateway'),
    path('transaction/<int:pk>/delete/', views.delete_transaction, name='delete-tx'),
    path('paket/<int:pk>/delete/', views.delete_paket, name='delete-paket'),
    path('ip/<int:pk>/delete/', views.delete_ip, name='delete-ip'),
    path('client/<int:pk>/delete/', views.delete_client, name='delete-client'),

    #detailPages
    path('server/id=<int:server_id>/', views.detailServer, name='detail-server'),

    path('client/id=<int:client_id>', views.detailClient, name='detail-client'),

    #==========================
    path('client/<int:client_id>/toggle/', views.toggle_activasi, name='toggle_activasi'),
    path('client/<int:client_id>/payment/', views.toggle_pembayaran, name='toggle_pembayaran'),

    # ==========================multi task==================
    path('client/activasi/multi', views.activasi_multi_client, name="activasi_multi"),

    path('client/handle-multiple/verif/', views.verif_multiple_client, name='verif_multiple'),
    path('client/handle-multiple/payment/', views.payment_multiple_client, name='payment_multiple'),
    path('client/handle-multiple/network/', views.net_multiple_client, name='net_multiple'),

    path('client/handle-multiple/delete/', views.delete_multiple_client, name='delete_multiple_client'),
    path('gateway/handle-multiple/delete/', views.delete_multiple_gateway, name='delete_multiple_gateway'),
    path('trans/handle-multiple/delete/', views.delete_multiple_transaction, name='delete_multiple_ts'),
    path('ip/handle-multiple/delete/', views.delete_multiple_ip, name='delete_multiple_ip'),
    path('paket/handle-multiple/delete/', views.delete_multiple_paket, name='delete_multiple_paket'),



    #========================other==============
    path('client/<int:client_id>/verification/', views.toggle_verif, name='toggle_verif'),
   
    path("test-conn/", views.test_conn_view, name="test_conn"),
    path("auto-conf/", views.auto_config, name="auto-conf"),


    path("client/reboot/", views.reboot, name="reboot"),

    path("api/", views.random_devices),

    path("api/client-remote/<int:client_id>/", views.get_client_remote, name="client-remote"),

    path("api/genieacs/<int:client_id>/", views.get_genieacs_data, name="get_genieacs_data"),



]


