from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
import requests

from app.templates.network.netmiko_service import cut_network

from .models import Client, Server, Redaman
from decouple import config

def set_status_false_and_notify():
    # Set semua pelanggan jadi belum bayar
    Client.objects.update(isPayed=False)

    # Kirim email notifikasi
    for p in Client.objects.all():
        send_mail(
            subject="Tagihan Internet Anda",
            message=f"Halo {p.name}, tagihan Anda sudah jatuh tempo. Mohon segera membayar sebelum tanggal {config('CUT_NETWORK_DATE')}.",
            from_email=config("DEFAULT_FROM_EMAIL"),
            recipient_list=[p.email],
        )
    print("Job tanggal", config("GIVE_NOTIF_DATE"), "dijalankan:", now())

def cut_connection_unpaid():
    unpaid = Client.objects.filter(isPayed=False)
    unpaid.update(isActive=False)
    data_client = []
    for p in unpaid:
        data_client.append({
            "pppoe": p.pppoe,        
            "host": p.id_paket.id_ip_pool.id_server.host,   
            "username": p.id_paket.id_ip_pool.id_server.username,  
            "password": p.id_paket.id_ip_pool.id_server.password,  
        })
    
    if data_client:
        results = cut_network(data_client)
        print("Cut connection results:", results)
    else:
        print("Tidak ada client yang belum bayar.")

    print("Job tanggal", config("CUT_NETWORK_DATE"), "dijalankan:", now())



def fetch_and_store_redaman():
    servers = Server.objects.exclude(genieacs__isnull=True).exclude(genieacs="")
    for srv in servers:
        url = (
            f"http://{srv.genieacs}:7557/devices"
            "?projection=VirtualParameters.redaman._value,"
            "VirtualParameters.pppoe._value"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            devices = response.json()

            for device in devices:
                vp = device.get("VirtualParameters", {})
                pppoe_val = vp.get("pppoe", {}).get("_value")
                redaman_val = vp.get("redaman", {}).get("_value")

                if not (pppoe_val and redaman_val):
                    continue

                client = Client.objects.filter(pppoe=pppoe_val).first()

                Redaman.objects.create(
                    id_client=client,
                    value=redaman_val
                )

            print(f"[OK] Redaman data stored from {srv.name} ({srv.genieacs})")

        except Exception as e:
            print(f"[ERROR] Failed fetching from {srv.name} ({srv.genieacs}): {e}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(set_status_false_and_notify, 'cron', day=int(config("GIVE_NOTIF_DATE")), hour=0, minute=0)
    scheduler.add_job(cut_connection_unpaid, 'cron', day=int(config("CUT_NETWORK_DATE")), hour=0, minute=0)

    scheduler.add_job(fetch_and_store_redaman, 'cron', hour=0, minute=0)



    # For testing
    run_time = now() + timedelta(seconds=5)
    # scheduler.add_job(set_status_false_and_notify, 'date', run_date=run_time)
    # scheduler.add_job(cut_connection_unpaid, 'date', run_date=run_time)

    # scheduler.add_job(fetch_and_store_redaman, 'date', run_date=run_time)


    scheduler.start()
