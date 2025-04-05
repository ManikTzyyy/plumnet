from routeros_api import RouterOsApiPool

api = RouterOsApiPool(
    host='192.168.0.133',
    username='manik',
    password='manik',
    port=8728,
    plaintext_login=True  # ⬅️ ini WAJIB diaktifkan di MikroTik versi baru
)

connection = api.get_api()

resource = connection.get_resource('/system/resource')
data = resource.get()[0]

print(data)
print("CPU Load:", data['cpu-load'])
print("Free Memory:", data['free-memory'])
print("Uptime:", data['uptime'])



# from routeros_api import RouterOsApiPool

# # Ganti sesuai konfigurasi kamu
# HOST = '192.168.0.133'
# USERNAME = 'manik'
# PASSWORD = 'manik'

# # Koneksi ke MikroTik
# api = RouterOsApiPool(
#     host=HOST,
#     username=USERNAME,
#     password=PASSWORD,
#     port=8728,
#     plaintext_login=True
# )
# connection = api.get_api()

# # Akses resource PPP secret (user pppoe)
# ppp_secret = connection.get_resource('/ppp/secret')

# # ✅ Tambah user PPPoE
# def tambah_user_pppoe(username, password, profile='default', service='pppoe'):
#     ppp_secret.add(
#         name=username,
#         password=password,
#         service=service,
#         profile=profile
#     )
#     print(f"✅ User PPPoE '{username}' berhasil ditambahkan.")

# # ✅ Tampilkan semua user PPPoE
# def tampilkan_user_pppoe():
#     users = ppp_secret.get()
#     print("📋 Daftar User PPPoE:")
#     for user in users:
#         print(f" - {user['name']} | Service: {user['service']} | Profile: {user['profile']}")

# # ❌ Hapus user PPPoE
# def hapus_user_pppoe(username):
#     users = ppp_secret.get(name=username)
#     if users:
#         ppp_secret.remove(id=users[0]['.id'])
#         print(f"❌ User PPPoE '{username}' berhasil dihapus.")
#     else:
#         print(f"⚠️ User '{username}' tidak ditemukan.")

# # ==== UJI COBA ====

# tambah_user_pppoe('ppptest1', 'tes123')
# tampilkan_user_pppoe()
# hapus_user_pppoe('ppptest1')
