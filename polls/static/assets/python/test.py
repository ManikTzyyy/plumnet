import socket
host = "192.168.0.131"
port = 8291

try:
    with socket.create_connection((host, port), timeout=5):
        print("Terkoneksi")
except Exception as e:
    print("Gagal konek:", e)
