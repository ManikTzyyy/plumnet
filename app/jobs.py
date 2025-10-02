from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
import requests
from django.utils import timezone
import urllib

from app.templates.network.netmiko_service import cut_network

from .models import Client, Server, Redaman
from decouple import config

# def set_status_false_and_notify():
#     # Set semua pelanggan jadi belum bayar
#     Client.objects.update(isPayed=False)

#     # Kirim email notifikasi
#     for p in Client.objects.all():
#         send_mail(
#             subject="Tagihan Internet Anda",
#             message=f"Halo {p.name}, tagihan Anda sudah jatuh tempo. Mohon segera membayar sebelum tanggal {config('CUT_NETWORK_DATE')}.",
#             from_email=config("DEFAULT_FROM_EMAIL"),
#             recipient_list=[p.email],
#         )
#     print("Job tanggal", config("GIVE_NOTIF_DATE"), "dijalankan:", now())

# def cut_connection_unpaid():
#     unpaid = Client.objects.filter(isPayed=False)
#     unpaid.update(isActive=False)
#     data_client = []
#     for p in unpaid:
#         data_client.append({
#             "pppoe": p.pppoe,        
#             "host": p.id_paket.id_ip_pool.id_server.host,   
#             "username": p.id_paket.id_ip_pool.id_server.username,  
#             "password": p.id_paket.id_ip_pool.id_server.password,  
#         })
    
#     if data_client:
#         results = cut_network(data_client)
#         print("Cut connection results:", results)
#     else:
#         print("Tidak ada client yang belum bayar.")

#     print("Job tanggal", config("CUT_NETWORK_DATE"), "dijalankan:", now())


def fetch_and_store_redaman():
    servers = Server.objects.exclude(genieacs__isnull=True).exclude(genieacs="")
    for srv in servers:
        clients = Client.objects.all()  # ambil semua client yang mau dicek

        for c in clients:
            query = {"VirtualParameters.pppoe._value": c.pppoe}
            query_str = urllib.parse.quote(str(query).replace("'", '"'))
            projection = (
                "VirtualParameters.redaman._value,"
                "VirtualParameters.pppoe._value"
            )
            url = f"http://{srv.genieacs}:7557/devices?query={query_str}&projection={projection}"

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
                    if client:
                        Redaman.objects.create(
                            id_client=client,
                            value=redaman_val
                        )

                print(f"[OK] Redaman data stored from {srv.name} ({srv.genieacs})")

            except Exception as e:
                print(f"[ERROR] Failed fetching from {srv.name} ({srv.genieacs}): {e}")


def process_billing_cycle():
    today = timezone.localdate()
    cut_after = int(config("CUT_NETWORK_AFTER", default=0))
    reminder_before_days = int(config("REMINDER_BEFORE_BILL", default=3))  

    for client in Client.objects.all():
        next_bill = client.get_next_bill_date()
        cut_date = next_bill + timedelta(days=cut_after)

        # === Reminder sebelum jatuh tempo ===
        if today == (next_bill - timedelta(days=reminder_before_days)) and client.isPayed:
            send_mail(
                subject="Pengingat Tagihan Internet Anda",
                message=(
                    f"Halo {client.name}, ini adalah pengingat bahwa tagihan Anda "
                    f"akan jatuh tempo pada {cut_date}. "
                    f"Silakan melakukan pembayaran sebelum tanggal tersebut agar layanan tetap aktif."
                ),
                from_email=config("DEFAULT_FROM_EMAIL"),
                recipient_list=[client.email],
            )
            client.isPayed = False
            client.save()
            print(f"[REMINDER] {client.name} - reminder terkirim ({reminder_before_days} hari sebelum jatuh tempo).")

        # === Hari cut: lakukan pemutusan ===
        if not client.isPayed and today >= cut_date and client.isActive:
            data_client = [{
                "pppoe": client.pppoe,
                "host": client.id_paket.id_ip_pool.id_server.host,
                "username": client.id_paket.id_ip_pool.id_server.username,
                "password": client.id_paket.id_ip_pool.id_server.password,
            }]
            results = cut_network(data_client)
            client.isActive = False
            client.save()
            status = results[0].get("status", "failed") if results else "failed"
            send_mail(
                subject="Layanan Internet Anda Dinonaktifkan",
                message=(
                    f"Halo {client.name}, layanan internet Anda telah dinonaktifkan pada {today} "
                    f"karena tagihan jatuh tempo tanggal {next_bill} belum dibayar. "
                    f"Silakan melakukan pembayaran agar layanan dapat diaktifkan kembali."
                ),
                from_email=config("DEFAULT_FROM_EMAIL"),
                recipient_list=[client.email],
            )
            print(f"[CUT] {client.name} - diputus pada {today}, results={status}, email terkirim.")





def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(set_status_false_and_notify, 'cron', day=int(config("GIVE_NOTIF_DATE")), hour=0, minute=0)
    # scheduler.add_job(cut_connection_unpaid, 'cron', day=int(config("CUT_NETWORK_DATE")), hour=0, minute=0)


    scheduler.add_job(process_billing_cycle, 'cron', hour=0, minute=0)

    scheduler.add_job(fetch_and_store_redaman, 'cron', hour=0, minute=0)



    # For testing
    run_time = now() + timedelta(seconds=5)
    # scheduler.add_job(set_status_false_and_notify, 'date', run_date=run_time)
    # scheduler.add_job(cut_connection_unpaid, 'date', run_date=run_time)
    scheduler.add_job(process_billing_cycle, 'date', run_date=run_time)

    # scheduler.add_job(fetch_and_store_redaman, 'date', run_date=run_time)


    scheduler.start()
