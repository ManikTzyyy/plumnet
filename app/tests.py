import random
from datetime import datetime, timedelta
from app.models import Redaman, Client  # ganti 'app' sesuai nama aplikasimu

# Ambil client id=2
client = Client.objects.get(id=2)

today = datetime.now()

for i in range(7):
    tanggal = today - timedelta(days=i)
    value = round(random.uniform(-50, 0), 2)  # angka desimal antara -50 sampai 0
    Redaman.objects.create(
        id_client=client,
        value=str(value),
        create_at=tanggal
    )

print("Data Redaman 7 hari terakhir berhasil dibuat untuk client 2!")
