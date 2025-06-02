import json, logging, socket, subprocess, paramiko
from django.contrib import messages


from .models import Paket, Server, IPPool, Client
from .mikrotik import get_mikrotik_info

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from polls.forms import ServerForm, PaketForm, ipPoolForm, ClientForm

from django.conf.urls import handler404


def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404

# Create your views here.

def get_server_info(request, server_id):
    try:
        server = Server.objects.get(id=server_id)
        info = get_mikrotik_info(server.host, server.username, server.password)
        return JsonResponse(info)
    except Server.DoesNotExist:
        raise Http404("Server not found")
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dashboard(request) : 
    servers = Server.objects.all()
    clients = Client.objects.all()
    query = request.GET.get('s', '')

    total_servers = Server.objects.count() 
    total_pakets = Paket.objects.count() 
    total_clients = Client.objects.count() 
    inactive_count = Client.objects.filter(isActive=0).count()

    if query:
        clients = clients.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_server__name__icontains=query)|
            Q(id_paket__name__icontains=query)
        )

    paginator = Paginator(clients, 10) 
    page_number = request.GET.get('page') 
    clients = paginator.get_page(page_number)


    context = {
        'total_servers' : total_servers,
        'total_pakets' : total_pakets,
        'total_clients' : total_clients,
        'inactive_clients' : inactive_count,
        'servers' : servers,
        'query' : query,
        'clients' : clients
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
    ip_pools = IPPool.objects.all()


    if query:
        paket_list = paket_list.filter(
            Q(name__icontains=query) | 
            Q(price__icontains=query) | 
            Q(limit__icontains=query)
        ) # Jika tidak ada pencarian, tampilkan semua data

    paginator = Paginator(paket_list, 10) 
    page_number = request.GET.get('page') 
    pakets = paginator.get_page(page_number) 

    return render(request, 'pages/paket.html', {'pakets': pakets, 'ip_pools':ip_pools, 'query': query})

def client(request) : 
    query = request.GET.get('s', '')
    client_list = Client.objects.all()

    if query:
        client_list = client_list.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_server__name__icontains=query)|
            Q(id_paket__name__icontains=query)
        )

    paginator = Paginator(client_list, 10) 
    page_number = request.GET.get('page') 
    clients = paginator.get_page(page_number)


    return render(request, 'pages/client.html', {'clients': clients, 'query': query})

def verifikasi(request) : 
    inactiveClient = Client.objects.filter(isActive=0)
    query = request.GET.get('s', '')

    if query:
        inactiveClient = inactiveClient.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_server__name__icontains=query)|
            Q(id_paket__name__icontains=query)
        ) 

    paginator = Paginator(inactiveClient, 10) 
    page_number = request.GET.get('page') 
    inactiveClient = paginator.get_page(page_number)

    context = {
        'query' : query,
        'clients' : inactiveClient
    }

    return render(request, 'pages/verifikasi.html',context)


#forms

def addServer(request):
    if request.method == "POST":
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('server') 
    else:
        form = ServerForm()

    return render(request, 'form-pages/form-server.html', {'form': form})

def addProfile(request) : 
    if request.method == "POST":
        form = PaketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paket') 
    else:
        form = PaketForm()

    return render(request, 'form-pages/form-profile.html', {'form': form})

def addIp(request) : 
    if request.method == "POST":
        form = ipPoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paket')
    else:
        form = ipPoolForm()

    return render(request, 'form-pages/form-ip.html', {'form': form})

def addClient(request) : 
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client')
    else:
        form = ClientForm()

    return render(request, 'form-pages/form-client.html', {'form': form})


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

def edit_paket(request, pk):
    paket = get_object_or_404(Paket, pk=pk)

    if request.method == 'POST':
        form = PaketForm(request.POST, instance=paket)
        if form.is_valid():
            form.save()
            return redirect('paket')  
    else:
        form = PaketForm(instance=paket)

    return render(request, 'form-pages/form-profile.html', {'form': form, 'is_edit': True})


def edit_ip(request, pk):
    ip_pool = get_object_or_404(IPPool, pk=pk)

    if request.method == 'POST':
        form = ipPoolForm(request.POST, instance=ip_pool)
        if form.is_valid():
            form.save()
            return redirect('paket')  
    else:
        form = ipPoolForm(instance=ip_pool)

    return render(request, 'form-pages/form-ip.html', {'form': form, 'is_edit': True})


def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client')  
    else:
        form = ClientForm(instance=client)

    return render(request, 'form-pages/form-client.html', {'form': form, 'is_edit': True})


#delete data

def delete_server(request, pk):
    server = get_object_or_404(Server, pk=pk)
    
    if request.method == "POST":
        server.delete()
        messages.success(request, "Server berhasil dihapus.")
        return redirect('server')  
    
    return redirect('detail-server', pk=pk)



def delete_paket(request, pk):
    paket = get_object_or_404(Paket, pk=pk)
    
    if request.method == "POST":
        paket.delete()
        messages.success(request, "Paket berhasil dihapus.")
        return redirect('paket')  
    
    return redirect('paket', pk=pk)

def delete_ip(request, pk):
    ip_pool = get_object_or_404(IPPool, pk=pk)
    
    if request.method == "POST":
        ip_pool.delete()
        messages.success(request, "IP Pool berhasil dihapus.")
        return redirect('paket')  
    
    return redirect('paket', pk=pk)

def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == "POST":
        client.delete()
        messages.success(request, "IP Pool berhasil dihapus.")
        return redirect('client')  
    
    return redirect('client', pk=pk)

#detail

def detailServer(request, server_id) : 
    server = get_object_or_404(Server, id=server_id)
    return render(request, 'detail-pages/detail-server.html', {'server': server})



def detailClient(request, client_id) : 
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'detail-pages/detail-client.html',{'client': client})

#=========================================================================

def toggle_activasi(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.isActive = not client.isActive
    client.save()
    return redirect('verifikasi')

def toggle_activasi_client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.isActive = not client.isActive
    client.save()
    return redirect('detail-client',client_id=client.id)



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






logger = logging.getLogger(__name__)

BAD_COMMANDS = ['reboot', 'shutdown', 'halt', 'poweroff', 'logout', 'exit']

def execute_command(host, username, password, command):
    output = ""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect with timeout and without looking for SSH keys
        client.connect(
            hostname=host,
            username=username,
            password=password,
            look_for_keys=False,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command, timeout=15)
        output = stdout.read().decode() + stderr.read().decode()

    except Exception as e:
        logger.error(f"[SSH ERROR] {e}")
        output = f"SSH Error: {str(e)}"

    finally:
        client.close()

    return output

def send_command(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            command = data.get("command", "").strip()
            server_id = data.get("server_id")

            # Validasi perintah berbahaya
            for bad_cmd in BAD_COMMANDS:
                if bad_cmd in command.lower():
                    return JsonResponse({
                        "output": f"Perintah '{bad_cmd}' tidak diizinkan demi keamanan."
                    }, status=400)

            # Validasi input
            if not command:
                return JsonResponse({"output": "Perintah tidak boleh kosong."}, status=400)

            server = Server.objects.get(id=server_id)

            logger.info(f"[SEND_COMMAND] Eksekusi command ke server {server.host}: {command}")

            output = execute_command(server.host, server.username, server.password, command)

            return JsonResponse({"output": output or "Tidak ada output dari perintah."})

        except Server.DoesNotExist:
            return JsonResponse({"output": "Server tidak ditemukan."}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"output": "Format request tidak valid."}, status=400)

        except Exception as e:
            logger.exception("[ERROR] Gagal mengirim perintah")
            return JsonResponse({"output": f"Exception: {str(e)}"}, status=500)

    return JsonResponse({"output": "Hanya menerima metode POST."}, status=405)
