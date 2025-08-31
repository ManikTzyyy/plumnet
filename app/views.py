# Standard library
from datetime import timedelta
import random
import json
import logging
import subprocess
import urllib.parse

# Third-party
import requests
import paramiko
from django.utils import timezone
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf.urls import handler404

# Project imports
from mysite import settings
from app.forms import ServerForm, PaketForm, ipPoolForm, ClientForm
from app.utils.utlis import parse_mikrotik_output
from app.templates.network.netmiko_service import (
    clear_config,
    connect_network,
    create_auto_config,
    create_pool,
    create_pppoe,
    create_profile,
    cut_network,
    delete_pool,
    delete_pppoe,
    delete_profile,
    edit_pool,
    edit_pppoe,
    edit_profile,
    test_conn,
)
from .templates.network.routeros_service import get_mikrotik_info
from .models import Paket, Redaman, Server, IPPool, Client



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

    filter_value = request.GET.get('filter', '')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page <= 0: 
            per_page = 10
    except ValueError:
        per_page = 10

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

    if filter_value == "online":
        clients = clients.filter(isActive=True)
    elif filter_value == "offline":
        clients = clients.filter(isActive=False)
    elif filter_value == "done":
        clients = clients.filter(isPayed=True)
    elif filter_value == "waiting":
        clients = clients.filter(isPayed=False)

    paginator = Paginator(clients, per_page) 
    page_number = request.GET.get('page') 
    clients = paginator.get_page(page_number)

    # try:
    #     response = requests.get("http://localhost:8000/api/")
    #     response.raise_for_status()
    #     acs_json = response.json()
    # except Exception as e:
    #     print("Error fetch ACS API:", e)
    #     acs_json = []
    # if isinstance(acs_json, list):
    #     acs_data_map = {
    #         item["VirtualParameters"]["IDPPPoE"]["_value"].strip(): item["VirtualParameters"]
    #         for item in acs_json
    #     }
    # elif isinstance(acs_json, dict):
    #     acs_data_map = {k.strip(): v for k, v in acs_json.items()}
    # else:
    #     acs_data_map = {}

    # for client in clients:
    #     vp = acs_data_map.get(client.pppoe.strip())
    #     # print(client.pppoe, "=>", vp)
    #     if vp:
    #         client.rxpower = vp["RXpower"]["_value"]
    #         client.host_active = vp["hostActive"]["_value"]
    #         client.ip_tr069 = vp["ipTR069"]["_value"]
    #     else:
    #         client.rxpower = "-"
    #         client.host_active = "-"
    #         client.ip_tr069 = "-"


    context = {
        'total_servers' : total_servers,
        'total_pakets' : total_pakets,
        'total_clients' : total_clients,
        'inactive_clients' : inactive_count,
        'servers' : servers,
        'query' : query,
        'clients' : clients,
        'page_number':per_page,
        'filter': filter_value
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
    filter_value = request.GET.get('filter', '')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page <= 0:  # minimal 1
            per_page = 10
    except ValueError:
        per_page = 10

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

    if filter_value == "online":
        client_list = client_list.filter(isActive=True)
    elif filter_value == "offline":
        client_list = client_list.filter(isActive=False)
    elif filter_value == "done":
        client_list = client_list.filter(isPayed=True)
    elif filter_value == "waiting":
        client_list = client_list.filter(isPayed=False)

    paginator = Paginator(client_list, per_page) 
    page_number = request.GET.get('page') 
    clients = paginator.get_page(page_number)

    context = {
        'clients': clients, 
        'query': query,
        'page_number' : per_page,
        'filter':filter_value
        }


    return render(request, 'pages/client.html', context )



def verifikasi(request) : 
    inactiveClient = Client.objects.filter(isActive=0)
    query = request.GET.get('s', '')
    filter_value = request.GET.get('filter', '')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page <= 0:  # minimal 1
            per_page = 10
    except ValueError:
        per_page = 10

    if query:
        inactiveClient = inactiveClient.filter(
            Q(name__icontains=query)| 
            Q(address__icontains=query)| 
            Q(phone__icontains=query)| 
            Q(pppoe__icontains=query)| 
            Q(id_paket__name__icontains=query)
        ) 
    
    
    if filter_value == "done":
        inactiveClient = inactiveClient.filter(isPayed=True)
    elif filter_value == "waiting":
        inactiveClient = inactiveClient.filter(isPayed=False)

    paginator = Paginator(inactiveClient, per_page) 
    page_number = request.GET.get('page') 
    inactiveClient = paginator.get_page(page_number)

    context = {
        'query' : query,
        'clients' : inactiveClient,
        'page_number' : per_page,
        'filter':filter_value
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
    
    genieACS = client.id_paket.id_ip_pool.id_server.genieacs
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    redaman_records = Redaman.objects.filter(
        id_client=client,
        create_at__date__range=[seven_days_ago, today]
    ).order_by('create_at')

    redaman_dict = {record.create_at.date(): record.value for record in redaman_records}

    labels = []
    data_redaman = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%d-%b'))  # contoh: '01-Aug'
        data_redaman.append(float(redaman_dict.get(day, 0))) 

     

    if genieACS:

        try:
            query = {
                    "VirtualParameters.pppoe._value": client.pppoe
                    }
            projection = (
                        "VirtualParameters.remote._value,"
                        "VirtualParameters.redaman._value,"
                        "VirtualParameters.active._value,"
                        "VirtualParameters.pppoe._value,"
                        "VirtualParameters.temperature._value"
                    )
            query_str = urllib.parse.quote(str(query).replace("'", '"'))

            url = f"http://{genieACS}:7557/devices?query={query_str}&projection={projection}"

            getData = requests.get(url, timeout=10)
            getData.raise_for_status()  # lempar error kalau status bukan 200
            data = getData.json()
            print(data)

            if data:
                device = data[0]   # ambil device pertama
                vp = device.get("VirtualParameters", {})
                client.redaman = vp.get("redaman", {}).get("_value", "-")
                client.active = vp.get("active", {}).get("_value", "-")
                client.remote = vp.get("remote", {}).get("_value", "-")
                client.temperature = vp.get("temperature", {}).get("_value", "-")
            else:
                client.redaman = '-'
                client.active = '-'
                client.remote = '-'
                client.temperature = '-'

        except Exception as e:
            print("Error fetch ACS API:", e)

    context = {
        'client': client,
        'labels': labels,
        'redaman_data': data_redaman,
    }

    return render(request, 'detail-pages/detail-client.html',context)


def map(request):
    clients = Client.objects.all().values("name", "lat", "long")
    context = {
        "clients_json": json.dumps(list(clients), cls=DjangoJSONEncoder)
    }
    return render(request, "pages/maps.html", context)

#=========================================================================
def activasi_multi_client(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Anda harus login dahulu untuk melakukan verifikasi."}, status=401)

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        results = connect_network(data)

        final_results = []
        for item, res in zip(data, results):
            client = Client.objects.filter(pppoe=item["pppoe"]).first()
            if not client:
                final_results.append({
                    "name": item['name'],
                    "pppoe": item["pppoe"],
                    "host": item["host"],
                    "status": "Client tidak ditemukan di DB",
                    "db_update": "FAILED",
                    "mikrotik": res
                })
                continue

            if res["status"] == "success":
                client.isActive = True
                client.save()
                final_results.append({
                    "name": item['name'],
                    "pppoe": item["pppoe"],
                    "host": item["host"],
                    "status": "Aktivasi berhasil",
                    "db_update": "OK",
                    "mikrotik": res
                })
            else:
                final_results.append({
                    "name": item['name'],
                    "pppoe": item["pppoe"],
                    "host": item["host"],
                    "status": f"{res['status']}",
                    "db_update": "FAILED",
                    "mikrotik": res
                })
               

        return JsonResponse({"success": True, "message": "Proses aktivasi multi selesai", "results": final_results})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e) or "Terjadi kesalahan saat memproses verifikasi."}, status=500)


def toggle_activasi(request, client_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Anda harus login dahulu untuk melakukan verifikasi."}, status=401)

    try:
        client = get_object_or_404(Client, id=client_id)
        paket = client.id_paket
        server = paket.id_ip_pool.id_server

        if client.isActive:
            result = cut_network([{
                "host": server.host,
                "username": server.username,
                "password": server.password,
                "pppoe": client.pppoe,
            }])
            if result[0].get("status") == "success":
                client.isActive = False
                client.save()
                msg = "Client berhasil dinonaktifkan"
            else:
                return JsonResponse({"success": False, "message": f"Gagal nonaktifkan: {result[0].get('error')}"})
        else:
            result = connect_network([{
                "host": server.host,
                "username": server.username,
                "password": server.password,
                "pppoe": client.pppoe,
                "profile": paket.name,
                "local_address": client.local_ip,
            }])
            if result[0].get("status") == "success":
                client.isActive = True
                client.save()
                msg = "Client berhasil diaktifkan"
            else:
                return JsonResponse({"success": False, "message": f"Gagal aktifkan: {result[0].get('error')}"})

        return JsonResponse({"success": True, "message": msg, "server_res": result})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e) or "Terjadi kesalahan saat memproses verifikasi."}, status=500)



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

        if client.isPayed:
            client.lastPayment = timezone.now().date()
            message = f"Pembayaran untuk {client.name} dikonfirmasi pada {client.lastPayment}."
        else:
            
            message = f"Tagihan untuk {client.name} berhasil dibuat."

        client.save()
        return JsonResponse({
            "success": True,
            "message": message
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



def random_devices(request):
    pppoe_ids = [
        "alex@plumnet",
        "agung@plumnet",
        "josep@plumnet",
        "cika@plumnet",
        "michael@plumnet"
    ]

    data = []
    for idx, pppoe in enumerate(pppoe_ids, start=1):
        data.append({
            "_id": str(idx),
            "VirtualParameters": {
                "RXpower": {"_value": f"{round(random.uniform(-20, -15), 2)}"},
                "ipTR069": {"_value": f"192.168.76.{random.randint(1,254)}"},
                "IDPPPoE": {"_value": pppoe},
                "hostActive": {"_value": str(random.randint(1, 10))}
            }
        })

    return JsonResponse(data, safe=False)










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