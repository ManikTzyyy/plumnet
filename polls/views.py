import socket
import subprocess
from django.contrib import messages

from .models import Paket, Server
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from polls.forms import ServerForm, PaketForm

# Create your views here.

def dashboard(request) : 
    total_servers = Server.objects.count() 
    total_pakets = Paket.objects.count() 
    context = {
        'total_servers' : total_servers,
        'total_pakets' : total_pakets,
    }
    return render(request, 'dashboard/dashboard.html', context)

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
    query = request.GET.get('search', '')  # Ambil query pencarian
    paket_list = Paket.objects.all()

    if query:
        paket_list = paket_list.filter(
            Q(name__icontains=query) | 
            Q(price__icontains=query) | 
            Q(limit__icontains=query)
        ) # Jika tidak ada pencarian, tampilkan semua data

    paginator = Paginator(paket_list, 10)  # Menampilkan 5 data per halaman
    page_number = request.GET.get('page')  # Ambil nomor halaman dari URL
    pakets = paginator.get_page(page_number)  # Ambil objek halaman

    return render(request, 'pages/paket.html', {'pakets': pakets, 'query': query})

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
    if request.method == "POST":
        form = PaketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paket')  # Ganti dengan nama URL yang sesuai
    else:
        form = PaketForm()

    return render(request, 'form-pages/form-profile.html', {'form': form})

def addClient(request) : 
    return render(request, 'form-pages/form-client.html')


#edit data
def edit_server(request, pk):
    server = get_object_or_404(Server, pk=pk)

    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            return redirect('server')  # Ubah ke URL yang sesuai dengan list server kamu
    else:
        form = ServerForm(instance=server)

    return render(request, 'form-pages/form-server.html', {'form': form, 'is_edit': True})


#delete data

def delete_server(request, pk):
    server = get_object_or_404(Server, pk=pk)
    
    if request.method == "POST":
        server.delete()
        messages.success(request, "Server berhasil dihapus.")
        return redirect('server')  
    
    return redirect('detail-server', pk=pk)


#detail

def detailServer(request, server_id) : 
    server = get_object_or_404(Server, id=server_id)
    return render(request, 'detail-pages/detail-server.html', {'server': server})



def detailClient(request) : 
    return render(request, 'detail-pages/detail-client.html')

#=========================================================================
def is_reachable(ip):
    try:
        subprocess.check_output(['ping', '-n', '1', '-w', '2000', ip])
        return True
    except subprocess.CalledProcessError:
        return False

def test_connection(request, pk):
    print(f"Test koneksi untuk server ID: {pk}")
    
    try:
        server = Server.objects.get(pk=pk)
        host = server.host
        port = 8291

        # Cek apakah bisa di-ping
        if not is_reachable(host):
            print(f"Host {host} tidak bisa diping")
            status = 'Tidak Aktif'
        else:
            print(f"Mencoba konek ke {host}:{port}")
            with socket.create_connection((host, port), timeout=2):
                print("Terkoneksi", host)
                status = 'Aktif'
    except Exception as e:
        print("Gagal konek:", e)
        status = 'Tidak Aktif'

    return JsonResponse({'status': status})
