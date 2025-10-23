# Standard library
from datetime import date, timedelta
import random
import json
import urllib.parse
from urllib.parse import quote


# Third-party
import requests
from django.db.models import F
from decouple import config
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
from app.forms import ConfigSystemForm, GatewayForm, ServerForm, PaketForm, ipPoolForm, ClientForm
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
    get_remote_from_mikrotik,
    test_conn,
)
from .templates.network.routeros_service import get_mikrotik_info
from .models import ConfigSystem, Gateway, Paket, Redaman, Server, IPPool, Client, Transaction




@login_required(login_url='/login/')
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


def update_config(request):
    config = ConfigSystem.objects.last() or ConfigSystem.objects.create()

    if request.method == "POST":
        form = ConfigSystemForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Config berhasil diperbarui"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    # kalau GET tetap render form biasa (opsional)
    form = ConfigSystemForm(instance=config)
    return render(request, "update_config.html", {"form": form})



@login_required(login_url='/login/')
def dashboard(request) : 
    servers = Server.objects.all()
    clients = Client.objects.all()
    

    total_servers = Server.objects.count() 
    total_pakets = Paket.objects.count() 
    total_clients = Client.objects.count() 
    inactive_count = Client.objects.filter(isActive=0).count()

    context = {
        'total_servers' : total_servers,
        'total_pakets' : total_pakets,
        'total_clients' : total_clients,
        'inactive_clients' : inactive_count,
        'servers' : servers,
        'clients' : clients,
    }
    
    return render(request, 'pages/dashboard.html', context)


@login_required(login_url='/login/')
def server(request):
    servers_list = Server.objects.all()
    return render(request, 'pages/server.html', {'servers': servers_list})


@login_required(login_url='/login/')
def paket(request) : 
   
    paket_list = Paket.objects.all()
    ip_pools = IPPool.objects.all()
    return render(request, 'pages/paket.html', {'pakets': paket_list, 'ip_pools':ip_pools,})


@login_required(login_url='/login/')
def client(request) : 
    client_list = Client.objects.all()
    context = {
        'clients': client_list, 
        }

    return render(request, 'pages/client.html', context )


@login_required(login_url='/login/')
def activasi(request) : 
    inactiveClient = Client.objects.filter(isActive=0)
    context = {
        'clients' : inactiveClient,
    }

    return render(request, 'pages/activasi.html',context)


#forms


@login_required(login_url='/login/')
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


# views.py

@login_required(login_url='/login/')
def addGateway(request, server_id):
    server = get_object_or_404(Server, pk=server_id)
    gateway_list = Gateway.objects.filter(server=server)
    gateway_qs = gateway_list.values("id", "name", "lat", "long", "parent_lat", "parent_long" )
    data = json.dumps(list(gateway_qs), cls=DjangoJSONEncoder)
    

    if request.method == "POST":
        form = GatewayForm(request.POST, server=server)
        if form.is_valid():
            gw = form.save(commit=False)
            parent_choice = form.cleaned_data.get("parent_choice")
            if parent_choice:
                if parent_choice.startswith("server-"):
                    # parent adalah server
                    gw.server = server
                    gw.parent_lat = server.lat
                    gw.parent_long = server.long
                elif parent_choice.startswith("odp-"):
                    # parent adalah ODP / gateway lain
                    gw_id = int(parent_choice.split("-")[1])
                    parent_gw = get_object_or_404(Gateway, id=gw_id)

                    # copy koordinat parent
                    gw.parent_lat = parent_gw.lat
                    gw.parent_long = parent_gw.long

                    # set server dari ODP
                    gw.server = parent_gw.server

            else:
                # default: server saat ini
                gw.server = server
                gw.parent_lat = server.lat
                gw.parent_long = server.long

            gw.save()
            messages.success(request, "ODP berhasil ditambahkan.")
            return redirect("detail-server", server_id=server.id)

        else:
            # handle error
            error_message = '\n'.join(
                f"{field}: {', '.join(errors)}"
                for field, errors in form.errors.items()
            )
            messages.error(request, f"Gagal menambahkan ODP:\n{error_message}")

    else:
        form = GatewayForm(server=server)

    context = {
        "form": form,
        "server": server,
        'data': data
    }
    return render(request, "form-pages/form-gateway.html", context)


@login_required(login_url='/login/')
def addProfile(request):
    success = False
    error_message = None
    infos = []
    successes = []

    if request.method == "POST":
        form = PaketForm(request.POST)
        if form.is_valid():
            limit = form.cleaned_data['limit']
            pools = form.cleaned_data['id_ip_pool']
            profile_base_name = form.cleaned_data['name']
            price = form.cleaned_data['price']


            errors = []
            for ip_pool in pools:
                
                server = ip_pool.id_server
                profile_name = f"{profile_base_name}-{ip_pool.name}"

                if Paket.objects.filter(name=profile_name, id_ip_pool=ip_pool).exists():
                    infos.append(f"{profile_name} sudah ada")
                    continue

                paket = Paket(
                    name=profile_name,
                    price=price,
                    limit=limit,
                    id_ip_pool=ip_pool  # single instance, aman
                )

                try:
                    # print(f"Membuat profile {profile_name} di pool {ip_pool.name} -> server {server.host}")
                    create_profile(
                        server.host,
                        server.username,
                        server.password,
                        profile_name,
                        ip_pool.name,
                        limit
                    )
                    paket.save()
                    successes.append(profile_name)
                except Exception as e:
                    infos.append(f"{profile_name}: {str(e)}")
            
            if successes and infos:
                info_message = "Beberapa profile berhasil dibuat, beberapa sudah ada atau gagal:\n"
                info_message += "Berhasil: " + ", ".join(successes) + "\n"
                info_message += "Info: " + ", ".join(infos)
                success = True
            elif successes:
                info_message = "Berhasil membuat profile: " + ", ".join(successes)
                success = True
            else:
                info_message = "Tidak ada profile baru yang berhasil dibuat.\n" + ", ".join(infos)
                success = False

            return render(request, 'form-pages/form-profile.html', {
                'form': form,
                'success': success,
                'info_message': info_message
            })

        else:
            error_message = "\n".join(
                f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()
            )
            return render(request, 'form-pages/form-profile.html', {
                'form': form,
                'success': False,
                'info_message': error_message
            })
    else:
        form = PaketForm()

    return render(request, 'form-pages/form-profile.html', {
        'form': form,
    })


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def addClient(request) : 

    servers = Server.objects.all().values("id", 'name', 'lat', 'long')
    gateways = Gateway.objects.all().values("id", "name", "lat", "long", "parent_lat", "parent_long")

    success = False
    error_message = None
    if request.method == "POST":
        paket_id = request.POST.get('id_paket')
        paket = Paket.objects.get(pk=paket_id) if paket_id else None
        
        ip_pool = getattr(paket, 'id_ip_pool', None)
        server = getattr(ip_pool, 'id_server', None)
        ip_range = getattr(ip_pool, 'ip_range', None)

        local_ip = None
        if ip_range:
            start_ip = ip_range.split("-")[0].strip()   # ambil "10.10.2.2"
            parts = start_ip.split(".")
            if len(parts) == 4:
                local_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"   # hasil "10.10.2.1"
        else:
            local_ip = None

       
        form = ClientForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if not cd.get('id_paket'):
                error_message = "Paket tidak boleh kosong."

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
                    local_ip=local_ip,
                    temp_paket=cd['id_paket'],
                    temp_name=cd['name'],
                    temp_address=cd['address'],
                    temp_phone=cd['phone'],
                    temp_pppoe=cd['pppoe'],
                    temp_password=cd['password'],
                    temp_local_ip=local_ip,
                    temp_lat=cd['lat'],
                    temp_long=cd['long'],
                    gateway=Gateway.objects.get(id=cd['gateway_choice']) if cd.get('gateway_choice') else None
                    )
            try:
                create_pppoe(
                    server.host,
                    server.username,
                    server.password,
                    cd['pppoe'],
                    cd['password'],
                    paket.name,
                    local_ip
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

    context = {''
    'form': form, 
    'success': success, 
    'error_message':error_message,
    "servers_json": json.dumps(list(servers), cls=DjangoJSONEncoder),
    "gateways_json": json.dumps(list(gateways), cls=DjangoJSONEncoder),
    }

    return render(request, 'form-pages/form-client.html', context)


#edit data
@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def edit_gateway(request, server_id, pk):
    success = False
    error_message = None
    server = get_object_or_404(Server, pk=server_id)
    gateway = get_object_or_404(Gateway, pk=pk)
    gateway_list = Gateway.objects.filter(server=server)
    gateway_qs = gateway_list.values("id", "name", "lat", "long", "parent_lat", "parent_long" )
    data = json.dumps(list(gateway_qs), cls=DjangoJSONEncoder)

    if request.method == 'POST':
        form = GatewayForm(request.POST, instance=gateway, server=server)
        if form.is_valid():
            gw = form.save(commit=False)
            parent_choice = form.cleaned_data.get("parent_choice")
            
            if parent_choice:
                if parent_choice.startswith("server-"):
                    # parent adalah server
                    gw.server = server
                    gw.parent_lat = server.lat
                    gw.parent_long = server.long
                elif parent_choice.startswith("odp-"):
                    # parent adalah ODP / gateway lain
                    gw_id = int(parent_choice.split("-")[1])
                    parent_gw = get_object_or_404(Gateway, id=gw_id)

                    # copy koordinat parent
                    gw.parent_lat = parent_gw.lat
                    gw.parent_long = parent_gw.long

                    # set server dari ODP
                    gw.server = parent_gw.server
            else:
                # default: server saat ini
                gw.server = server
                gw.parent_lat = server.lat
                gw.parent_long = server.long

            gw.save()
            messages.success(request, "ODP berhasil diupdate.")
            success = True

            # redirect ke detail server setelah edit
            return redirect("detail-server", server_id=server.id)
        else:
            error_message = '\n'.join(
                f"{field}: {', '.join(errors)}"
                for field, errors in form.errors.items()
            )
            messages.error(request, f"Gagal mengupdate ODP:\n{error_message}")

    else:
        # untuk GET, form harus aware server supaya dropdown parent_choice benar
        form = GatewayForm(instance=gateway, server=server)

    context = {
        'form': form,
        'is_edit': True,
        'success': success,
        'server': server,
        'error_message': error_message,
        'data': data
    }
    return render(request, 'form-pages/form-gateway.html', context)


@login_required(login_url='/login/')
def edit_paket(request, pk):
    paket = get_object_or_404(Paket, pk=pk)
    info_message = ""
    success_flag = False
    old_name = paket.name

    if request.method == 'POST':
        form = PaketForm(request.POST, instance=paket, edit=True)
        
        if form.is_valid():
            limit = form.cleaned_data['limit']
            profile_name = form.cleaned_data['name']
            ip_pool = form.cleaned_data['id_ip_pool']

            if ip_pool is None:
                info_message = "IP Pool tidak boleh null."
            else:
                new_server = ip_pool.id_server
                if new_server is None:
                    info_message = "Tambahkan server pada IP Pool terlebih dahulu!"
                else:
                    current_server = paket.id_ip_pool.id_server if paket.id_ip_pool else None
                  

                    try:
                        if current_server is None:
                        
                            # buat profile baru
                            create_profile(new_server.host, new_server.username, new_server.password,
                                           profile_name, ip_pool.name, limit)
                            paket.id_ip_pool = ip_pool
                            paket.limit = limit
                            paket.save()
                            info_message = f"Profile '{profile_name}' berhasil dibuat."
                            success_flag = True
                        elif current_server != new_server:
                            info_message = "Tidak boleh mengganti IP Pool yang berbeda dengan server lama."
                        else:
                            # edit profile
              
                            edit_profile(new_server.host, new_server.username, new_server.password,
                                         profile_name, ip_pool.name, limit, old_name)
                            paket.id_ip_pool = ip_pool
                            paket.limit = limit
                            paket.save()
                            info_message = f"Profile '{profile_name}' berhasil diupdate."
                            success_flag = True
                    except Exception as e:
                        info_message = f"Gagal: {str(e)}"
        else:
            info_message = "\n".join(f"{field}: {', '.join(errors)}" for field, errors in form.errors.items())

        return render(request, 'form-pages/form-profile.html', {
            'form': form,
            'paket': paket,
            'success': success_flag,
            'info_message': info_message,
            'is_edit': True
        })

    else:
        form = PaketForm(instance=paket, edit=True)

    return render(request, 'form-pages/form-profile.html', {
        'form': form,
        'is_edit': True
    })


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    success = False
    error_message = None
    local_ip = None


    servers = Server.objects.all().values("id", 'name', 'lat', 'long')
    gateways = Gateway.objects.all().values("id", "name", "lat", "long", "parent_lat", "parent_long")

    if request.method == 'POST':
        paket_id = request.POST.get('id_paket')
        current_server = client.id_paket.id_ip_pool.id_server if client.id_paket else None       
        paket = Paket.objects.get(pk=paket_id) if paket_id else None
        server = paket.id_ip_pool.id_server if paket else None

        ip_range = paket.id_ip_pool.ip_range if paket and paket.id_ip_pool else None
        if ip_range:
            start_ip = ip_range.split("-")[0].strip()   # contoh "10.10.2.2"
            parts = start_ip.split(".")
            if len(parts) == 4:
                local_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"

        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            cd = form.cleaned_data
            
            client.refresh_from_db(fields=['id_paket', 'name', 'address', 'email', 'phone','pppoe', 'password', 'lat', 'long'])


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
                    client.temp_local_ip = local_ip
                    client.isApproved = False
                    client.isServerNull = True
                    client.temp_gateway = Gateway.objects.get(id=cd['gateway_choice']) if cd.get('gateway_choice') else None
                   
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
                    client.temp_local_ip = local_ip
                    client.isApproved = False
                    client.temp_gateway = Gateway.objects.get(id=cd['gateway_choice']) if cd.get('gateway_choice') else None
                   
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
        "servers_json": json.dumps(list(servers), cls=DjangoJSONEncoder),
        "gateways_json": json.dumps(list(gateways), cls=DjangoJSONEncoder),
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



def delete_gateway(request, pk):
    gateway = get_object_or_404(Gateway, pk=pk)
    if request.method == "POST":
        try:
            res = 'Gateway Deleted'            
            gateway.delete()
            return JsonResponse({'success': True, 'message': res}) 
        except Exception as e:
            error_message = str(e) 
        
    return JsonResponse({'success': False, 'message': error_message}, status=400)



def delete_paket(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        res = delete_paket_internal(pk)
        return JsonResponse({"success": True, "message": res})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



def delete_ip(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        res = delete_ip_internal(pk)
        return JsonResponse({"success": True, "message": res})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



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



def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        try:
            res = 'Transaction Deleted'
            tx.delete()
            return JsonResponse({
                'success': True, 'message':res
            })
        except Exception as e:
            error_message = str(e)
            
    return JsonResponse({'success': False, 'message': error_message}, status=400) 
#detail



@login_required(login_url='/login/')
def detailServer(request, server_id) : 
    server = get_object_or_404(Server, id=server_id)
    gateway_list = Gateway.objects.filter(server=server)
    gateway_qs = gateway_list.values("id", "name", "lat", "long", "parent_lat", "parent_long" )
    data = json.dumps(list(gateway_qs), cls=DjangoJSONEncoder)
    context = {
        'server': server,
        'gateway_list': gateway_list,
        'data': data
        }
    return render(request, 'detail-pages/detail-server.html', context)



def get_client_remote(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    host = client.id_paket.id_ip_pool.id_server.host  # atau field server router kamu
    username = client.id_paket.id_ip_pool.id_server.username
    password = client.id_paket.id_ip_pool.id_server.password

    remote_ip = get_remote_from_mikrotik(host, username, password, client.pppoe)

    return JsonResponse({
        "pppoe": client.pppoe,
        "remote": remote_ip,
    })



def get_genieacs_data(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    genieACS = client.id_paket.id_ip_pool.id_server.genieacs if client.id_paket else None

    data = {
        "redaman": "-",
        "active": "-",
        "remote": "-",
        "temperature": "-",
        "device": "-"
    }

    if genieACS:
        try:
            query = {"VirtualParameters.pppoe._value": client.pppoe}
            projection = (
                "VirtualParameters.remote._value,"
                "VirtualParameters.redaman._value,"
                "VirtualParameters.active._value,"
                "VirtualParameters.pppoe._value,"
                "VirtualParameters.temperature._value,"
                "VirtualParameters.uptime._value"
            )
            query_str = urllib.parse.quote(str(query).replace("'", '"'))
            url = f"http://{genieACS}:7557/devices?query={query_str}&projection={projection}"

            r = requests.get(url, timeout=2)  # biar gak nunggu lama
            r.raise_for_status()
            resp = r.json()

            if resp:
                device = resp[0]
                vp = device.get("VirtualParameters", {})
                data = {
                    "uptime": vp.get("uptime", {}).get("_value", "-"),
                    "redaman": vp.get("redaman", {}).get("_value", "-"),
                    "active": vp.get("active", {}).get("_value", "-"),
                    "remote": vp.get("remote", {}).get("_value", "-"),
                    "temperature": vp.get("temperature", {}).get("_value", "-"),
                    "device": device.get("_id", "-")
                }
        except Exception as e:
            print("Error fetch ACS API",)

    return JsonResponse(data)



@login_required(login_url='/login/')
def detailClient(request, client_id): 
    client = get_object_or_404(Client, id=client_id)

    transaction = Transaction.objects.filter(id_client=client).order_by('-create_at')

    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    redaman_records = Redaman.objects.filter(
        id_client=client,
        create_at__date__range=[seven_days_ago, today]
    ).order_by("create_at")

    redaman_dict = {record.create_at.date(): record.value for record in redaman_records}

    labels, data_redaman = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%d-%b"))
        data_redaman.append(float(redaman_dict.get(day, 0)))

    # Default data GenieACS (biar halaman tetap kebuka cepat)
    client.redaman = "-"
    client.active = "-"
    client.remote = "-"
    client.temperature = "-"
    client.device = "-"


      # ambil transaksi terakhir
    last_tx = transaction.first()
    last_payment = last_tx.create_at.date() if last_tx else None
    next_bill = client.get_next_bill_date()


    acs_ip = client.id_paket.id_ip_pool.id_server.genieacs if client.id_paket else None

   

    context = {
        "client": client,
        "labels": labels,
        "redaman_data": data_redaman,
        'acs_ip':acs_ip,
        'transaction':transaction,
        "last_payment": last_payment,
        "next_bill": next_bill,
    }
    return render(request, "detail-pages/detail-client.html", context)


@login_required(login_url='/login/')
def map(request):
    servers = Server.objects.all().values("id", 'name', 'lat', 'long')
    gateways = Gateway.objects.all().values("id", "name", "lat", "long", "parent_lat", "parent_long")
    clients_qs = Client.objects.select_related('gateway').annotate(
    gateway_lat=F('gateway__lat'),
    gateway_long=F('gateway__long')
        ).values('id', 'name', 'lat', 'long', 'gateway_lat', 'gateway_long') 

    context = {
        "clients_json": json.dumps(list(clients_qs), cls=DjangoJSONEncoder),
        "servers_json": json.dumps(list(servers), cls=DjangoJSONEncoder),
        "gateways_json": json.dumps(list(gateways), cls=DjangoJSONEncoder),
    }
    return render(request, "pages/maps.html", context)



#=================================Multiple task========================================


def activasi_multi_client(request):
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
        return JsonResponse({"success": False, "message": str(e) or "Terjadi kesalahan saat memproses activasi."}, status=500)



def payment_multiple_client(request):

    datas = json.loads(request.body.decode("utf-8"))
    results = []

    for data in datas:
        client_id = data.get("id")
        name = data.get("name")

        try:
            message = toggle_pembayaran_internal(client_id)
            results.append({"name": name, "success": True, "message": message})
        except Exception as e:
            results.append({"name": name, "success": False, "message": str(e)})

    return JsonResponse({"success": True, "results": results})



def verif_multiple_client(request):
    datas = json.loads(request.body.decode("utf-8"))
    results = []

    for data in datas:
        client_id = data.get("id")
        name = data.get('name')

        try:
            message = toggle_verif_internal(client_id, request.user)
            results.append({"name": name, "success": True, "message": message})
        except Exception as e:
            results.append({"name": name, "success": False, "message": str(e)})

    return JsonResponse({"success": True, "results": results})



def net_multiple_client(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        datas = json.loads(request.body.decode("utf-8"))
        results = []

        for data in datas:
            client_id = data.get("id")
            name = data.get("name")

            try:
                message = toggle_activasi_internal(client_id)
                results.append({"name": name, "success": True, "message": message})
            except Exception as e:
                results.append({"name": name, "success": False, "message": str(e)})

        return JsonResponse({"success": True, "results": results})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e) or "Terjadi kesalahan."}, status=500)



def toggle_pembayaran_internal(client_id):
    client = get_object_or_404(Client, id=client_id)
    client.isPayed = not client.isPayed
    price = getattr(client.id_paket, "price", 0) or 0

    if client.isPayed:
        # buat record transaksi
        Transaction.objects.create(
            id_client=client,
            value=price
        )
        message = f"Pembayaran  berhasil dikonfirmasi!"
    else:
        message = f"Tagihan berhasil dibuat."

    client.save()
    return message



def toggle_verif_internal(client_id, user):

    client = get_object_or_404(Client, id=client_id)
    old_pppoe = client.pppoe
    paket = client.id_paket
    statusVerif = client.isApproved

    if statusVerif:
        raise Exception("Client sudah terverifikasi perubahannya")

    if not client.temp_paket:
        raise Exception("Client belum memilih paket sementara.")

    new_server = client.temp_paket.id_ip_pool.id_server
    new_paket = client.temp_paket

    # cek kalau pppoe sudah dipakai
    if not client.isApproved:
        if Client.objects.filter(Q(pppoe=client.temp_pppoe) & ~Q(id=client.id)).exists():
            raise Exception(f"ID PPPoE '{client.temp_pppoe}' sudah digunakan oleh client lain.")

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
    client.gateway = client.temp_gateway

    # toggle verif
    client.isServerNull = not client.isServerNull
    client.isApproved = not client.isApproved
    client.save()

    return (
        f"Client berhasil diverifikasi."
        if client.isApproved else
        f"Verifikasi untuk dibatalkan."
    )



def delete_ip_internal(ip_id):
    ip_pool = get_object_or_404(IPPool, pk=ip_id)
    server = ip_pool.id_server
    profile_data = list(
        Paket.objects.filter(id_ip_pool_id=ip_pool).values_list("name", flat=True)
    )

    if server:
        delete_pool(
            server.host,
            server.username,
            server.password,
            ip_pool.name,
            profile_data,
        )
        ip_pool.delete()
        return "IP Pool deleted (with server action)"
    else:
        ip_pool.delete()
        return "IP Pool deleted without server action"



def toggle_activasi_internal(client_id):
    client = get_object_or_404(Client, id=client_id)
    paket = client.id_paket
    server = paket.id_ip_pool.id_server

    if client.isActive:
        # Nonaktifkan client
        result = cut_network([{
            "host": server.host,
            "username": server.username,
            "password": server.password,
            "pppoe": client.pppoe,
        }])
        if result[0].get("status") == "success":
            client.isActive = False
            client.save()
            return "Client berhasil dinonaktifkan"
        else:
            raise Exception(f"Gagal nonaktifkan: {result[0].get('error')}")
    else:
        # Aktifkan client
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
            return "Client berhasil diaktifkan"
        else:
            raise Exception(f"Gagal aktifkan: {result[0].get('error')}")



def delete_multiple_client(request):
    data = json.loads(request.body.decode('utf-8'))
    results = []

    for client_data in data:
        client_id = client_data.get('id')
        name = client_data.get('name')
        host = client_data.get('host')
        username = client_data.get('username')
        password = client_data.get('password')
        pppoe = client_data.get('pppoe')

        try:
            client_obj = Client.objects.get(id=client_id)

            if host:
                try:
                    delete_pppoe(host, username, password, pppoe)
                    results.append({"name": name, "status": "success", "deleted_on_mikrotik": True, 'message': "Deleted with server Action"})
                except Exception as e:
                    results.append({"name": name, "status": "failed", "message": str(e)})
                    continue 
            client_obj.delete()
            if not host: 
                results.append({"name": name, "status": "success", "deleted_on_mikrotik": False, 'message': "Deleted without server Action"})

        except Client.DoesNotExist:
            results.append({"name": name, "status": "failed", "message": "Client tidak ditemukan"})

    return JsonResponse({"success": True, "results": results})



def delete_multiple_gateway(request):
    datas = json.loads(request.body.decode('utf-8'))
    results = []

    for data in datas:
        data_id = data.get('id')
        name = data.get('name')

        try:
            gw_object = Gateway.objects.get(id=data_id)
            results.append({"name": name, "status": "success", 'message': "Deleted"})
            gw_object.delete()

        except Gateway.DoesNotExist:
            results.append({"name": name, "status": "failed", "message": "Data tidak ditemukan"})

    return JsonResponse({"success": True, "results": results})



def delete_multiple_transaction(request):
    datas = json.loads(request.body.decode('utf-8'))
    results = []

    for data in datas:
        data_id = data.get('id')
        name = data.get('name')

        try:
            ts = Transaction.objects.get(id=data_id)
            results.append({"name": name, "status": "success", 'message': "Deleted"})
            ts.delete()

        except Gateway.DoesNotExist:
            results.append({"name": name, "status": "failed", "message": "Data tidak ditemukan"})

    return JsonResponse({"success": True, "results": results})



def delete_multiple_ip(request):
    datas = json.loads(request.body.decode("utf-8"))
    results = []

    for data in datas:
        ip_id = data.get("id")
        name = data.get('name')
        try:
            # panggil delete_ip internal function tanpa HTTP request
            res = delete_ip_internal(ip_id)
            results.append({"name": name, "success": True, "message": res})
        except Exception as e:
            results.append({"name": name, "success": False, "message": str(e)})

    return JsonResponse({"success": True, "results": results})



def delete_multiple_paket(request):
    datas = json.loads(request.body.decode("utf-8"))
    results = []

    for data in datas:
        paket_id = data.get("id")
        name = data.get('name')
        try:
            # panggil delete_ip internal function tanpa HTTP request
            res = delete_paket_internal(paket_id)
            results.append({"name": name, "success": True, "message": res})
        except Exception as e:
            results.append({"name": name, "success": False, "message": str(e)})

    return JsonResponse({"success": True, "results": results})



def delete_paket(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        res = delete_paket_internal(pk)
        return JsonResponse({"success": True, "message": res})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



def delete_paket_internal(paket_id):
    paket = get_object_or_404(Paket, pk=paket_id)
    ip_pool = paket.id_ip_pool
    server = ip_pool.id_server if ip_pool else None
    client_data = list(
        Client.objects.filter(id_paket_id=paket.id).values_list("pppoe", flat=True)
    )

    if server:
        delete_profile(
            server.host,
            server.username,
            server.password,
            paket.name,
            client_data,
        )
        paket.delete()
        return "Paket deleted (with server action)"
    else:
        paket.delete()
        return "Paket deleted without server action"

# =========================other===================================


def toggle_activasi(request, client_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        message = toggle_activasi_internal(client_id)
        return JsonResponse({"success": True, "message": message})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e) or "Terjadi kesalahan saat memproses activasi."
        }, status=500)



def toggle_verif(request, client_id):
    try:
        message = toggle_verif_internal(client_id, request.user)
        return JsonResponse({"success": True, "message": message})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)



def toggle_pembayaran(request, client_id):
    try:
        message = toggle_pembayaran_internal(client_id)
        return JsonResponse({"success": True, "message": message})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e) or "Terjadi kesalahan."
        }, status=500)




GENIEACS_USER = config("GENIEACS_USERNAME")
GENIEACS_PASS = config("GENIEACS_PASSWORD")




def reboot(request):
   
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            device = data.get("device")   # _id dari GenieACS device
            genieacs = data.get("genieacs")  # IP / hostname GenieACS server
         

            if not device or not genieacs:
                return JsonResponse({"status": "error", "message": "Device ID atau GenieACS tidak dikirim"}, status=400)

            device_id = quote(device, safe="")
            task_url = f"http://{genieacs}:7557/devices/{device_id}/tasks"
            payload = {"name": "reboot"}

            task_resp = requests.post(
                task_url,
                json=payload,
                auth=(GENIEACS_USER, GENIEACS_PASS),
                timeout=10
            )

           
            task_resp.raise_for_status()  # kalau error akan masuk ke except

            return JsonResponse({"status": "success", "message": f"Perangkat {device} sedang direboot"})

        except requests.RequestException as e:
            return JsonResponse({"status": "error", "message": f"Gagal kirim perintah reboot: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)



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
                "RXpower": {"_value": f"{round(random.uniform(-25, -10), 2)}"},
                "ipTR069": {"_value": f"192.168.76.{random.randint(1,254)}"},
                "IDPPPoE": {"_value": pppoe},
                "hostActive": {"_value": str(random.randint(1, 10))}
            }
        })

    return JsonResponse(data, safe=False)


def get_theme_settings():
    with open(settings.BASE_DIR / 'static' / 'setting.json') as f:
        return json.load(f)