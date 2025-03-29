from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def dashboard(request) : 
    return render(request, 'dashboard/dashboard.html')

def server(request) : 
    return render(request, 'pages/server.html')

def paket(request) : 
    return render(request, 'pages/paket.html')

def client(request) : 
    return render(request, 'pages/client.html')

def verifikasi(request) : 
    return render(request, 'pages/verifikasi.html')

def setting(request) : 
    return render(request, 'pages/setting.html')

def informasi(request) : 
    return render(request, 'pages/info.html')

#forms

def addServer(request) : 
    return render(request, 'form-pages/form-server.html')

def addProfile(request) : 
    return render(request, 'form-pages/form-profile.html')

def addClient(request) : 
    return render(request, 'form-pages/form-client.html')


#detail

def detailServer(request) : 
    return render(request, 'detail-pages/detail-server.html')

def detailClient(request) : 
    return render(request, 'detail-pages/detail-client.html')