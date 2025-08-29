import json, logging, socket, subprocess, paramiko
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.decorators import login_required

from mysite import settings
from app.templates.network.netmiko_service import clear_config, connect_network, create_auto_config, create_pool, create_pppoe, create_profile, cut_network, delete_pool, delete_pppoe, delete_profile, edit_pool, edit_pppoe, edit_profile, set_disabled_pppoe, test_conn
from app.utils.utlis import parse_mikrotik_output
from .templates.network.routeros_service import get_mikrotik_info

from .models import Paket, Server, IPPool, Client

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from app.forms import ServerForm, PaketForm, ipPoolForm, ClientForm

from django.conf.urls import handler404





def get_server_info(request, server_id):
    try:
        server = Server.objects.get(id=server_id)
        info = get_mikrotik_info(server.host, server.username, server.password)
        client_count = Client.objects.filter(id_paket__id_ip_pool__id_server=server).count()
        client_active =  Client.objects.filter(id_paket__id_ip_pool__id_server=server,  isActive=True).count()
        info['client_count'] = client_count
        info['client_active'] = client_active
        return JsonResponse(info)
    except Server.DoesNotExist:
        return JsonResponse({"error": "Server not found"}, status=404)
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

    query_lower = query.strip().lower()

    status_filter = Q()
    if query_lower == "online":
        status_filter = Q(isActive=True)
    elif query_lower == "offline":
        status_filter = Q(isActive=False)

    if query:
        clients = clients.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_paket__name__icontains=query)|
            Q(id_paket__id_ip_pool__id_server__name__icontains=query)|
            status_filter
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
    return render(request, 'pages/dashboard.html', context)



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

    query_lower = query.strip().lower()

    status_filter = Q()
    if query_lower == "online":
        status_filter = Q(isActive=True)
    elif query_lower == "offline":
        status_filter = Q(isActive=False)

    if query:
        client_list = client_list.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_paket__name__icontains=query) | 
            Q(id_paket__id_ip_pool__id_server__name__icontains=query) |
            status_filter
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
    success = False
    error_message = None
    if request.method == "POST":
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            # return redirect('server') 
        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = ServerForm()

    return render(request, 'form-pages/form-server.html', {'form': form, 'success': success, 'error_message':error_message})

def addProfile(request) :
    success = False
    error_message = None 
    if request.method == "POST":
        form = PaketForm(request.POST)
        if form.is_valid():
            limit = form.cleaned_data['limit']
            profile_name = form.cleaned_data['name']
            ip_pool = form.cleaned_data['id_ip_pool']
            server = ip_pool.id_server
            try:
                # print(limit, profile_name, server.name, server.host)

                create_profile(
                    server.host,
                    server.username,
                    server.password,
                    profile_name,
                    ip_pool.name,
                    limit
                )
                form.save()
                success = True
            except Exception as e:
                error_message = str(e) 
            

        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = PaketForm()

    return render(request, 'form-pages/form-profile.html', {
        'form': form,
        'success': success, 
        'error_message':error_message
        })

def addIp(request) : 
    success = False
    error_message = None 
    if request.method == "POST":
        form = ipPoolForm(request.POST)
        if form.is_valid():
            server = form.cleaned_data['id_server']
            pool_name = form.cleaned_data['name']
            pool_range = form.cleaned_data['ip_range']
            try:
                create_pool(
                    server.host, 
                    server.username, 
                    server.password,
                    pool_name,
                    pool_range
                    )
                form.save()
                success = True
            except Exception as e:
                error_message = str(e)        
        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = ipPoolForm()

    return render(request, 'form-pages/form-ip.html', {
        'form': form,
        'success': success, 
        'error_message':error_message
        })

def addClient(request) : 
    success = False
    error_message = None
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            paket = cd['id_paket']
            server = paket.id_ip_pool.id_server
            client = Client(
                    id_paket=cd['id_paket'],
                    name=cd['name'],
                    address=cd['address'],
                    email=cd['email'],
                    phone=cd['phone'],
                    pppoe=cd['pppoe'],
                    password=cd['password'],
                    lat=cd['lat'],
                    long=cd['long'],
                    local_ip=cd['local_ip'],
                    temp_paket=cd['id_paket'],
                    temp_name=cd['name'],
                    temp_address=cd['address'],
                    temp_phone=cd['phone'],
                    temp_pppoe=cd['pppoe'],
                    temp_password=cd['password'],
                    temp_local_ip=cd['local_ip'],
                    temp_lat=cd['lat'],
                    temp_long=cd['long']
                    )
            try:
                create_pppoe(
                    server.host,
                    server.username,
                    server.password,
                    cd['pppoe'],
                    cd['password'],
                    paket.name,
                    cd['local_ip']
                )
                
                client.save()
                success = True
            except Exception as e:
                error_message = str(e) 
            
        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = ClientForm()

    return render(request, 'form-pages/form-client.html', {'form': form, 'success': success, 'error_message':error_message})


#edit data
def edit_server(request, pk):
    success = False
    error_message = None
    server = get_object_or_404(Server, pk=pk)

    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            success = True
        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = ServerForm(instance=server)

    return render(request, 'form-pages/form-server.html', {
        'form': form,
        'is_edit': True,
        'success': success,
        'error_message': error_message
        })

def edit_paket(request, pk):
    success = False
    error_message = None
    paket = get_object_or_404(Paket, pk=pk)
    current_server = paket.id_ip_pool.id_server if paket.id_ip_pool else None
    current_profile = paket.name if paket.name else None

    if request.method == 'POST':
        form = PaketForm(request.POST, instance=paket)

        if form.is_valid():
            limit = form.cleaned_data['limit']
            profile_name = form.cleaned_data['name']
            ip_pool = form.cleaned_data['id_ip_pool']
            if ip_pool == None:
                error_message = "IP Pool tidak boleh Null"          
            else:
                new_server = ip_pool.id_server
                if new_server == None:
                    error_message = "Tambahkan Server pada IP Pool Terlebih Dahulu!"
                else:
                    try:
                        if current_server is None:
                            create_profile(new_server.host,new_server.username,new_server.password,profile_name,ip_pool.name,limit,)
                            form.save()
                            success = True
                        elif current_server != new_server:
                            error_message = "Tidak boleh mengganti IP Pool yang berbeda dengan server lama."
                        else:
                            edit_profile(new_server.host,new_server.username,new_server.password,profile_name,ip_pool.name,limit,current_profile)
                            form.save()
                            success = True 
                    except Exception as e:
                        error_message = str(e) 
        else:
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = PaketForm(instance=paket)

    return render(request, 'form-pages/form-profile.html', {
        'form': form, 
        'is_edit': True,
        'success': success,
        'error_message': error_message
        })


def edit_ip(request, pk):
    success = False
    error_message = None

    ip_pool = get_object_or_404(IPPool, pk=pk)
    current_pool = ip_pool.name
    server = ip_pool.id_server
    

    if request.method == 'POST':
        form = ipPoolForm(request.POST, instance=ip_pool)
        if form.is_valid():
            pool_name = form.cleaned_data['name']
            pool_range = form.cleaned_data['ip_range']
            new_server = form.cleaned_data['id_server']

            if new_server is None:
                error_message = "Server tidak boleh kosong."
            else:
                try:
                    if server is None:
                        # kasus: belum ada server → boleh create pool
                        create_pool(
                            new_server.host, 
                            new_server.username, 
                            new_server.password,
                            pool_name, 
                            pool_range
                        )
                        form.save()
                        success = True

                    elif server != new_server:
                        # kasus: server lama ada, tapi user coba ganti → error
                        error_message = "Tidak boleh mengganti server lama."

                    else:
                        # kasus: server lama sama → boleh edit pool
                        edit_pool(
                            server.host, 
                            server.username, 
                            server.password,
                            pool_name, 
                            pool_range, 
                            current_pool
                        )
                        form.save()
                        success = True

                except Exception as e:
                    error_message = str(e)
        else:
            # gabung error form
            error_message = ''
            for field, errors in form.errors.items():
                error_message += f"{field}: {', '.join(errors)}\n"
    else:
        form = ipPoolForm(instance=ip_pool)

    return render(request, 'form-pages/form-ip.html', {
        'form': form,
        'is_edit': True,
        'success': success,
        'error_message': error_message
    })


def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    success = False
    error_message = None

    if request.method == 'POST':
    
        current_server = client.id_paket.id_ip_pool.id_server if client.id_paket else None       
        form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            cd = form.cleaned_data
            
            client.refresh_from_db(fields=['id_paket', 'name', 'address', 'email', 'phone','pppoe', 'password', 'lat', 'long', 'local_ip'])


            new_paket = form.cleaned_data['id_paket']
            new_server = new_paket.id_ip_pool.id_server if new_paket else None
            
            if new_server == None:
                error_message = "Paket tidak boleh kosong."
            elif current_server is None:
                try:
                    client.temp_paket = new_paket
                    client.temp_name = cd['name']
                    client.temp_address = cd['address']
                    client.temp_phone = cd['phone']
                    client.temp_email = cd['email']
                    client.temp_pppoe = cd['pppoe']
                    client.temp_password = cd['password']
                    client.temp_lat = cd['lat']
                    client.temp_long = cd['long']
                    client.temp_local_ip = cd['local_ip']
                    client.isApproved = False
                    client.isServerNull = True
                   
                    client.save()
                    success = True
                except Exception as e:
                    error_message = str(e)
                
            elif new_server !=  current_server:
                error_message = 'Tidak boleh mengganti paket ke server berbeda!'
            else:
                try:
                    client.temp_paket = new_paket
                    client.temp_name = cd['name']
                    client.temp_address = cd['address']
                    client.temp_phone = cd['phone']
                    client.temp_email = cd['email']
                    client.temp_pppoe = cd['pppoe']
                    client.temp_password = cd['password']
                    client.temp_lat = cd['lat']
                    client.temp_long = cd['long']
                    client.temp_local_ip = cd['local_ip']
                    client.isApproved = False
                   
                    client.save()
                    success = True
                except Exception as e:
                    error_message = str(e)
        else:
            error_message = "\n".join(
                [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
            )
    else:
        form = ClientForm(instance=client)

    return render(request, 'form-pages/form-client.html', {
        'form': form,
        'is_edit': True,
        'success': success,
        'error_message': error_message,
    })





#delete data

def delete_server(request, pk):
    server = get_object_or_404(Server, pk=pk)
    pool_data = list(IPPool.objects.filter(id_server=server).values_list('name', flat=True))
    profile_data = list(Paket.objects.filter(id_ip_pool__id_server=server).values_list('name', flat=True))
    client_data = list(Client.objects.filter(id_paket__id_ip_pool__id_server=server).values_list('pppoe', flat=True))
    if request.method == "POST":
        try:
            res = 'Server Deleted'
            clear_config(
                server.host, 
                server.username, 
                server.password,
                pool_data,
                profile_data,
                client_data
            )
            
            server.delete()
            return JsonResponse({'success': True, 'message': res}) 
        except Exception as e:
            error_message = str(e) 
        
    return JsonResponse({'success': False, 'message': error_message}, status=400)



def delete_paket(request, pk):
    res = None
    paket = get_object_or_404(Paket, pk=pk)
    current_profile = paket.name
    ip_pool = paket.id_ip_pool
    server = ip_pool.id_server if ip_pool else None
    client_data = list(Client.objects.filter(id_paket_id=paket.id).values_list('pppoe', flat=True))
    # print(client_data)
    if request.method == "POST":
        try:
            # print(server)
            if server != None:
                res = 'Paket deleted'
                delete_profile(server.host, server.username, server.password,current_profile,client_data)
                paket.delete()
            else:
                res = 'Paket deleted without server action'
                paket.delete()
            return JsonResponse({'success': True, 'message': res }) 
        except Exception as e:
                error_message = str(e) 
    return JsonResponse({'success': False, 'message': error_message}, status=400)

def delete_ip(request, pk):
    ip_pool = get_object_or_404(IPPool, pk=pk)
    server = ip_pool.id_server
    current_pool = ip_pool.name
    profile_data = list(Paket.objects.filter(id_ip_pool_id=ip_pool).values_list('name', flat=True))
    if request.method == "POST":
        try:
            if server != None:
                res = 'IP Pool deleted'
                delete_pool(server.host, server.username, server.password, current_pool, profile_data)
                ip_pool.delete()
            else:
                res = 'Pool deleted without server action'
                ip_pool.delete()
            return JsonResponse({'success': True, 'message': res})
        except Exception as e:
                error_message = str(e) 
    return JsonResponse({'success': False, 'message': error_message}, status=400)

def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == "POST":
        paket = client.id_paket
        server = paket.id_ip_pool.id_server if paket else None
        try:
            if server != None:
                res = 'Client deleted'
                delete_pppoe( server.host, server.username, server.password,client.pppoe)            
                client.delete()
            else:
                res = 'Client deleted without server action'
                client.delete()
            return JsonResponse({'success': True, 'message': res})
        except Exception as e:
                error_message = str(e) 
       
    
    return JsonResponse({'success': False, 'message': error_message}, status=400)

#detail

def detailServer(request, server_id) : 
    server = get_object_or_404(Server, id=server_id)
    return render(request, 'detail-pages/detail-server.html', {'server': server})



def detailClient(request, client_id) : 
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'detail-pages/detail-client.html',{'client': client})


def map(request):
    clients = Client.objects.all().values("name", "lat", "long")
    context = {
        "clients_json": json.dumps(list(clients), cls=DjangoJSONEncoder)
    }
    return render(request, "pages/maps.html", context)

#=========================================================================

def toggle_activasi(request, client_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Anda harus login dahulu untuk melakukan verifikasi."
        }, status=401)

    try:
        client = get_object_or_404(Client, id=client_id)
        paket = client.id_paket
        server = paket.id_ip_pool.id_server
      

        if client.isActive:
            result = cut_network(server.host, server.username, server.password, [client.pppoe])
            client.isActive = False
            msg = 'Client berhasil dinonaktifkan'
        else:
            result = connect_network(server.host, server.username, server.password, [{"name":client.pppoe, "profile": paket.name, "local_address":client.local_ip }])
            client.isActive = True
            msg ="Client berhasil diaktifkan"
    
        client.save()

        return JsonResponse({
            "success": True,
            "message": msg,
            "server_res": result
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e) or "Terjadi kesalahan saat memproses verifikasi."
        }, status=500)


def toggle_verif(request, client_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Anda harus login dahulu untuk melakukan verifikasi."
        }, status=401)

    try:
        client = get_object_or_404(Client, id=client_id)
        old_pppoe = client.pppoe
        paket = client.id_paket

        # pastikan temp_paket ada
        if not client.temp_paket:
            return JsonResponse({
                "success": False,
                "message": "Client belum memilih paket sementara."
            }, status=400)

        new_server = client.temp_paket.id_ip_pool.id_server
        new_paket = client.temp_paket

        # cek kalau pppoe sudah dipakai
        if not client.isApproved:
            if Client.objects.filter(Q(pppoe=client.temp_pppoe) & ~Q(id=client.id)).exists():
                return JsonResponse({
                    "success": False,
                    "message": f"ID PPPoE '{client.temp_pppoe}' sudah digunakan oleh client lain."
                })

        if paket is None:
            # create baru
            create_pppoe(
                new_server.host,
                new_server.username,
                new_server.password,
                client.temp_pppoe,
                client.temp_password,
                new_paket.name,
                client.temp_local_ip
            )
            client.id_paket = new_paket
            client.name = client.temp_name
            client.address = client.temp_address
            client.email = client.temp_email
            client.phone = client.temp_phone
            client.pppoe = client.temp_pppoe
            client.password = client.temp_password
            client.local_ip = client.temp_local_ip
            client.lat = client.temp_lat
            client.long = client.temp_long
            
        else:
            # edit existing
            edit_pppoe(
                new_server.host,
                new_server.username,
                new_server.password,
                client.temp_pppoe,
                client.temp_password,
                new_paket.name,
                client.temp_local_ip,
                old_pppoe
            )

            # update data client
            client.id_paket = new_paket
            client.name = client.temp_name
            client.address = client.temp_address
            client.email = client.temp_email
            client.phone = client.temp_phone
            client.pppoe = client.temp_pppoe
            client.password = client.temp_password
            client.local_ip = client.temp_local_ip
            client.lat = client.temp_lat
            client.long = client.temp_long

        # toggle verif
        client.isServerNull = not client.isServerNull
        client.isApproved = not client.isApproved
        client.save()

        return JsonResponse({
            "success": True,
            "message": (
                f"Client {client.name} berhasil diverifikasi."
                if client.isApproved else
                f"Verifikasi untuk {client.name} dibatalkan."
            )
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error internal: {str(e)}"
        }, status=500)


def toggle_pembayaran(request, client_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Anda harus login dahulu."
        }, status=401)

    try:
        client = get_object_or_404(Client, id=client_id)
        client.isPayed = not client.isPayed
        client.save()
        return JsonResponse({
            "success": True,
            "message": "Client berhasil diaktifkan." if client.isPayed else "Client berhasil dinonaktifkan."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e) or "Terjadi kesalahan."
        }, status=500)



def is_reachable(ip):
    try:
        subprocess.check_output(['ping', '-n', '1', '-w', '2000', ip])
        return True
    except subprocess.CalledProcessError:
        return False


def test_conn_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        host = data.get("host")
        username = data.get("username")
        password = data.get("password")
        try:
            res = test_conn(host, username, password)
            parse_mikrotik_output(res)
            return JsonResponse({"success": True, "message": res})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {e}"})

    return JsonResponse({"success": False, "message": "Invalid request"})


def auto_config(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        host=data.get('host')
        interfaceHost = data.get("hostEther")
        username = data.get("username")
        oldPassword = data.get("oldPassword")
        password = data.get("password")
        interfacePPPoE = data.get("pppoeEther")
        try:
            res = create_auto_config(
                host, 
                interfaceHost, 
                username, 
                oldPassword,
                password, 
                interfacePPPoE
                )

            server = Server.objects.create(
                name=f"Router-{host}",  # kamu bisa kasih input `name` dari form kalau mau
                host=host,
                username=username,
                password=password,
            )

            server.save()
            return JsonResponse({"success": True, "message": res})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {e}"})  
         
    return JsonResponse({"success": False, "message": "Invalid request"})  


logger = logging.getLogger(__name__)

BAD_COMMANDS = ['reboot', 'shutdown', 'ping' 'halt', 'poweroff', 'logout', 'exit']

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


def get_theme_settings():
    with open(settings.BASE_DIR / 'static' / 'setting.json') as f:
        return json.load(f)