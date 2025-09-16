import django
import telebot
from decouple import config
import requests
import threading

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from app.models import Server



API_TOKEN = config("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
PORT = config("PORT" , default=7557, cast=int)
TARGET_CHAT_ID = config("TARGET_CHAT_ID")

# ---------- CEK GENIEACS SERVER ----------

def fetch_genieacs_server():
    seen = set()
    results = {}
    for srv in Server.objects.exclude(genieacs__isnull=True).exclude(genieacs__exact=''):
        ip = srv.genieacs.strip()

        if ip in seen:
            continue
        seen.add(ip)

        target = f'http://{ip}:{PORT}'
        try: 
            r = requests.get(target, timeout=3)
            results[ip]=('ok', f"HTTP {r.status_code} {r.reason}")
        except requests.exceptions.Timeout:
            results[ip]=('timeout', 'Request timed out after {timeout} s')
        except requests.exceptions.ConnectionError as e:
            results[ip]=('connect err', str(e))
        except requests.exceptions.RequestException as e:
            results[ip]=('err', str(e))
    return results

@bot.message_handler(commands=['cek_genieacs'])
def cek_genieacs(message):
    results = fetch_genieacs_server()
    if not results:
        bot.reply_to(message, "No Server with valid GenieACS IP found.")
        return
    msg = ['GenieACS Server Check:']
    for ip, (status, detail) in results.items():
        msg.append(f"{ip} - {status.upper()}: {detail}")
    bot.reply_to(message, "\n".join(msg))

# ---------- FUNGSI FETCH ----------
# def fetch_data(url):
#     try:
#         response = requests.get(url, timeout=5)
#         response.raise_for_status()
#         return response
#     except requests.exceptions.RequestException as e:
#         print(f"[API ERROR] {e}")
#         return e 


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
f"""
Howdy! Use /help to see available commands.
Your chat_id is: {message.chat.id}
""")


# ---------- HELP ----------
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Available commands:
/help - Show this menu
/cek_genieacs - Show GenieACS Server status
/cek_device <page> - List devices (paginated), per page = 20 device
/cek_redaman - Show devices with redaman 
/cek_user <username> - Find device by PPPoE user
"""
    bot.reply_to(message, help_text)


# ---------- PAGINATION ----------
@bot.message_handler(commands=['cek_device'])
def cek_device(message):
    try:
        page = int(message.text.split()[1])  # /cek_device 2
    except (IndexError, ValueError):
        page = 1
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page

    servers = fetch_genieacs_server()
    active = [ip for ip, (status, _) in servers.items() if status == "ok"]
    if not active:
        bot.reply_to(message, "⚠️ Tidak ada server GenieACS yang aktif.")
        return
    base_url = f"http://{active[0]}:{PORT}"
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"⚠️ API ERROR di {active[0]}: {e}")
        return

    devices = response.json()[start:end]
    hasil = []
    for dev in devices:
        vp = dev["VirtualParameters"]
        hasil.append(
            f"""
Uptime: {vp['uptime']['_value']}
PPPOE: {vp['pppoe']['_value']}
IP Remote: {vp['remote']['_value']}
Redaman: {vp['redaman']['_value']}
Temperatur: {vp['temperature']['_value']}C
"""
        )
    pesan = "\n".join(hasil) if hasil else "No data on this page."
    bot.reply_to(message, pesan)


# ---------- REDAMAN ----------
@bot.message_handler(commands=['cek_redaman'])
def cek_redaman(message):

    servers = fetch_genieacs_server()
    active = [ip for ip, (status, _) in servers.items() if status == "ok"]
    if not active:
        bot.reply_to(message, "⚠️ Tidak ada server GenieACS yang aktif.")
        return
    base_url = f"http://{active[0]}:{PORT}"
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"⚠️ API ERROR di {active[0]}: {e}")
        return

    devices = response.json()
    hasil = []
    for dev in devices:
        vp = dev["VirtualParameters"]
        rx_power = float(vp["redaman"]["_value"])
        user = vp["pppoe"]["_value"]
        ip = vp["remote"]["_value"]

        # klasifikasi sesuai standar jurnal & FTTH
        if rx_power <= -25:
            status = "🚨 CRITICAL (sinyal terlalu lemah, ≤ -25 dBm)"
        elif -25 < rx_power <= -18:
            status = "⚠️ Warning (sinyal lemah, -25 s/d -18 dBm)"
        elif -18 < rx_power <= -13:
            status = "✅ Normal (rentang ideal -18 s/d -13 dBm)"
        else:  # rx_power > -13
            status = "⚠️ Warning (sinyal terlalu kuat, > -13 dBm)"

        hasil.append(
            f"{status}\nUser: {user}\nIP: {ip}\nRX Power: {rx_power} dBm"
        )

    pesan = "\n\n".join(hasil) if hasil else "Tidak ada data."
    bot.reply_to(message, pesan)


# ---------- CEK USER ----------
@bot.message_handler(commands=['cek_user'])
def cek_user(message):
    try:
        keyword = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Usage: /cek_user <username>")
        return

    servers = fetch_genieacs_server()
    active = [ip for ip, (status, _) in servers.items() if status == "ok"]
    if not active:
        bot.reply_to(message, "⚠️ Tidak ada server GenieACS yang aktif.")
        return
    base_url = f"http://{active[0]}:{PORT}"
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"⚠️ API ERROR di {active[0]}: {e}")
        return

    devices = response.json()
    hasil = []
    for dev in devices:
        vp = dev["VirtualParameters"]
        if keyword.lower() in vp["pppoe"]["_value"].lower():
            hasil.append(
                f"{vp['pppoe']['_value']} | IP: {vp['remote']['_value']} | RX: {vp['redaman']['_value']}"
            )
    pesan = "\n".join(hasil) if hasil else f"No user found with {keyword}"
    bot.reply_to(message, pesan)


def auto_check_redaman(interval=300):
    print('Checking Redaman Data.........')
    """
    Jalan setiap `interval` detik (default 5 menit).
    Cek semua server aktif, lalu kirim notifikasi kalau ada redaman parah.
    """
    servers = fetch_genieacs_server()
    active = [ip for ip, (status, _) in servers.items() if status == "ok"]

    if not active:
        # bot.send_message(TARGET_CHAT_ID, "⚠️ Tidak ada server GenieACS yang aktif untuk pengecekan redaman.")
        print("No active server")
    else:
        for ip in active:
            base_url = f"http://{ip}:{PORT}"
            try:
                response = requests.get(base_url, timeout=5)
                response.raise_for_status()
                devices = response.json()
            except requests.exceptions.RequestException as e:
                # bot.send_message(TARGET_CHAT_ID, f"⚠️ API ERROR di {ip}: {e}")
                print("API ERROR", e)
                continue

            hasil = []
            for dev in devices:
                vp = dev["VirtualParameters"]
                rx_power = float(vp["redaman"]["_value"])
                user = vp["pppoe"]["_value"]
                ipaddr = vp["remote"]["_value"]

                if rx_power <= -25:
                    status = "🚨 CRITICAL (≤ -25 dBm)"
                    hasil.append(f"{status}\nUser: {user}\nIP: {ipaddr}\nRX Power: {rx_power} dBm")


            if hasil:
                pesan = "⚠️ Deteksi Redaman Buruk:\n\n" + "\n\n".join(hasil)
                bot.send_message(TARGET_CHAT_ID, pesan)
            else:
                print("Redaman aman")

    # jadwalkan lagi
    threading.Timer(interval, auto_check_redaman, [interval]).start()


print("Bot is running...")
auto_check_redaman(interval=config("INTERVAL_CHECK", default=300, cast=int))
bot.infinity_polling()
