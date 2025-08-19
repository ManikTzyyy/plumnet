from django.test import TestCase
from netmiko import ConnectHandler
import ipaddress


host = "192.168.2.1"   
hostEther = "ether2"
newUsername = "admin"
newPassword = "admin"
etherPPPoE = "ether5"

mikrotik = {
    "device_type": "mikrotik_routeros",
    "ip": host,
    "username": "admin",
    "password": "",  
    "port": 22,
}

net_connect = ConnectHandler(**mikrotik)
print("✅ Berhasil connect ke Mikrotik")


net_connect.send_config_set([
    "/ip dhcp-client add interface=ether1 disabled=no"
])


net_connect.send_config_set([
    "/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1"
])


output = net_connect.send_command(f"/ip address print where interface={hostEther}")
print(f"IP di {hostEther} :\n{output}")


ip_cidr = None
for line in output.splitlines():
    if "/" in line and "ADDRESS" not in line:
        parts = line.split()
        ip_cidr = parts[1]  
        break

if not ip_cidr:
    print(f"❌ Interface {hostEther} belum ada IP. Set dulu sebelum lanjut.")
else:
    ip_iface = ipaddress.ip_interface(ip_cidr)
    network = ip_iface.network
    gateway = str(ip_iface.ip)

    hosts = list(network.hosts())
    if len(hosts) >= 2:
        start_ip = str(hosts[1])   
        end_ip   = str(hosts[-1])  
        pool_range = f"{start_ip}-{end_ip}"

        net_connect.send_config_set([
            f"/ip pool add name=dhcp_pool ranges={pool_range}",
            f"/ip dhcp-server add name=dhcp1 interface={hostEther} address-pool=dhcp_pool disabled=no",
            f"/ip dhcp-server network add address={network.with_prefixlen} gateway={gateway} dns-server=8.8.8.8"
        ])

        print(f"✅ DHCP server aktif di {hostEther}, range {pool_range}")
    else:
        print("❌ Network terlalu kecil, tidak bisa bikin pool DHCP")


net_connect.send_config_set([
    f"/interface pppoe-server server add service-name=pppoe_server interface={etherPPPoE} disabled=no"
])
print(f"✅ PPPoE server aktif di {etherPPPoE}")


if newUsername != "admin" or newPassword != "":
    net_connect.send_config_set([
        f"/user set [find name=admin] name={newUsername} password={newPassword}"
    ])
    print("✅ Username & password berhasil diupdate")

net_connect.disconnect()
print("Auto Config selesai")
