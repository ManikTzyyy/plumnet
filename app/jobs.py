from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

from app.templates.network.netmiko_service import cut_network

from .models import Client
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

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(set_status_false_and_notify, 'cron', day=int(config("GIVE_NOTIF_DATE")), hour=0, minute=0)
    scheduler.add_job(cut_connection_unpaid, 'cron', day=int(config("CUT_NETWORK_DATE")), hour=0, minute=0)
    
    
    
    # For testing
    # run_time = now() + timedelta(minutes=1)
    # scheduler.add_job(set_status_false_and_notify, 'date', run_date=run_time)
    # scheduler.add_job(cut_connection_unpaid, 'date', run_date=run_time)

    scheduler.start()
