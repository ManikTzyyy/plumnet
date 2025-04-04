from .models import Server
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from polls.forms import ServerForm

# Create your views here.

def dashboard(request) : 
    return render(request, 'dashboard/dashboard.html')

def server(request):
    query = request.GET.get('search', '')  # Ambil query pencarian
    servers_list = Server.objects.all()

    if query:
        servers_list = servers_list.filter(
            Q(name__icontains=query) | 
            Q(host__icontains=query) | 
            Q(username__icontains=query) | 
            Q(genieacs__icontains=query)
        ) # Jika tidak ada pencarian, tampilkan semua data

    paginator = Paginator(servers_list, 10)  # Menampilkan 5 data per halaman
    page_number = request.GET.get('page')  # Ambil nomor halaman dari URL
    servers = paginator.get_page(page_number)  # Ambil objek halaman

    return render(request, 'pages/server.html', {'servers': servers, 'query': query})

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

def addServer(request):
    if request.method == "POST":
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('server')  # Ganti dengan nama URL yang sesuai
    else:
        form = ServerForm()

    return render(request, 'form-pages/form-server.html', {'form': form})

def addProfile(request) : 
    return render(request, 'form-pages/form-profile.html')

def addClient(request) : 
    return render(request, 'form-pages/form-client.html')


#detail

def detailServer(request, server_id) : 
    server = get_object_or_404(Server, id=server_id)
    return render(request, 'detail-pages/detail-server.html', {'server': server})

def detailClient(request) : 
    return render(request, 'detail-pages/detail-client.html')