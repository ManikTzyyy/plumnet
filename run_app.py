import webview
import subprocess
import socket
import time
import atexit

django_process = None

def start_django():
    global django_process
    django_process = subprocess.Popen(
        "python manage.py runserver",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True  # Penting agar Windows lebih gampang kelola proses
    )

def stop_django():
    global django_process
    if django_process:
        print("Mematikan server Django...")
        django_process.kill()
        django_process.wait()

def tunggu_django_ready(host='127.0.0.1', port=8000, timeout=10):
    print("Menunggu server Django siap...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("Server Django siap!")
                return True
                
        except OSError:
            time.sleep(0.5)
    
    return False

# Pastikan server mati saat program selesai
atexit.register(stop_django)

# Start Django
start_django()

# Tunggu server siap
if tunggu_django_ready():
    webview.create_window("My Django App", "http://127.0.0.1:8000", width=1024, height=768)
    webview.start()
else:
    print("Gagal konek ke server Django.")
