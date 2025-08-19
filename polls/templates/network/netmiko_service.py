import ipaddress
from netmiko import ConnectHandler


def get_mikrotik_conn (host, username, password):
    device = {
        'device_type' : 'mikrotik_routeros',
        'host' : host,
        'username' : username,
        'password' : password,
    }
    return  ConnectHandler(**device)



def test_conn(host, username, password):  
        conn = get_mikrotik_conn(host, username, password)
        output = conn.send_command("/system resource print")
        conn.disconnect()
        return output




def clear_config(host, username, password, pools=None, profiles=None):
    try:
        conn = get_mikrotik_conn(host, username, password)

        if pools:
            for pool_item in pools:
                command = f'/ip pool remove [find name="{pool_item}"]'
                conn.send_command(command)
        if profiles:
            for profile_item in profiles:
                command = f'/ppp profile remove [find name="{profile_item}"]'
                conn.send_command(command)
                
        conn.disconnect()
        return True

    except Exception as e:
        raise Exception(f"Error: {e}")


# IP Pool Service
def create_pool(host, username, password, pool_name, ip_range):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ip pool add name={pool_name} ranges={ip_range}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal membuat IP pool: {e}")
    

def edit_pool(host, username, password, pool_name, ip_range, current_pool):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ip pool set {current_pool} name={pool_name} ranges={ip_range}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal edit IP pool: {e}")


def delete_pool(host, username, password, current_pool, profiles):

    try:
        conn = get_mikrotik_conn(host, username, password)

        
        if profiles:
            for profile_item in profiles:
                command = f'/ppp profile remove [find name="{profile_item}"]'
                conn.send_command(command)
        
        command_pool = f"/ip pool remove {current_pool}"
        output = conn.send_command(command_pool)

        conn.disconnect()
        return output
    

    except Exception as e:
        raise Exception(f"Gagal hapus IP pool: {e}")
    

def create_profile(host, username, password, profile_name, pool_name, limit):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp profile add name={profile_name} remote-address={pool_name} rate-limit={limit}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal membuat Profile: {e}")


def edit_profile(host, username, password, profile_name, pool_name, limit, current_profile):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp profile set {current_profile} name={profile_name} remote-address={pool_name} rate-limit={limit}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal edit Profile: {e}")
    
def delete_profile(host, username, password, current_profile):
    
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp profile remove {current_profile}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal hapus Profile: {e}")
    

def create_pppoe(host, username, password, pppoe, password_pppoe, profile, local_ip):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp secret add name={pppoe} password={password_pppoe} profile={profile} local-address={local_ip} service=pppoe disabled=yes"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal membuat PPPoE: {e}")


def edit_pppoe(host, username, password, pppoe, password_pppoe, profile, local_ip, current_pppoe):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp secret set {current_pppoe} name={pppoe} password={password_pppoe}, profile={profile} local-address={local_ip} service=pppoe"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal edit PPPoE: {e}")
    
def delete_pppoe(host, username, password, current_pppoe):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp secret remove {current_pppoe}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f'Gagal hapus PPPoE : {e}')

        

def set_disabled_pppoe(host, username, password, pppoe, status):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ppp secret set {pppoe} disabled={status}"
        output = conn.send_command(command)
        conn.disconnect()
        return output
    except Exception as e:
        raise Exception(f"Gagal activasi PPPoE: {e}")
    


def create_auto_config(host, interfaceHost, newUser,oldPass, newPass, interfacePPPoE):
    device = {
        "device_type": "mikrotik_routeros",
        "ip": host,
        "username": "admin",
        "password": oldPass,  
    }

    try:
        # Connect
        net_connect = ConnectHandler(**device)
        print("✅ Connected to MikroTik Router", flush=True)

        # DHCP client on ether1
        print("🔄 Enabling DHCP client on ether1...", flush=True)
        net_connect.send_config_set(["/ip dhcp-client add interface=ether1 disabled=no"])
        print("✅ DHCP client enabled on ether1", flush=True)
        net_connect.send_config_set(["/ip dhcp-client print"]),

        # NAT masquerade
        print("🔄 Setting NAT masquerade on ether1...", flush=True)
        net_connect.send_config_set(["/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1"])
        print("✅ NAT masquerade configured", flush=True)

        # DNS
        print("🔄 Setting DNS servers (8.8.8.8, 8.8.4.4)...", flush=True)
        net_connect.send_config_set(['/ip dns set servers=8.8.8.8,8.8.4.4'])
        print("✅ DNS servers configured", flush=True)

        # DHCP Server on interfaceHost
        print(f"🔄 Checking IP address on {interfaceHost}...", flush=True)
        output = net_connect.send_command(f"/ip address print where interface={interfaceHost}")

        ip_cidr = None
        for line in output.splitlines():
            if "/" in line and "ADDRESS" not in line:
                parts = line.split()
                ip_cidr = parts[1]
                break

        if not ip_cidr:
            print(f"❌ No IP address found on {interfaceHost}, please configure manually first.", flush=True)
        else:
            ip_iface = ipaddress.ip_interface(ip_cidr)
            network = ip_iface.network
            gateway = str(ip_iface.ip)

            hosts = list(network.hosts())
            if len(hosts) >= 2:
                start_ip = str(hosts[1])   # biasanya .2
                end_ip   = str(hosts[-1])  # biasanya .254
                pool_range = f"{start_ip}-{end_ip}"

                print(f"🔄 Creating IP pool for {interfaceHost} ({pool_range})...", flush=True)
                net_connect.send_config_set([
                    f"/ip pool add name=dhcp_pool ranges={pool_range}",
                ])
                print(f"✅ IP pool created: {pool_range}", flush=True)

                print(f"🔄 Configuring DHCP server on {interfaceHost}...", flush=True)
                net_connect.send_config_set([
                    f"/ip dhcp-server add name=dhcp1 interface={interfaceHost} address-pool=dhcp_pool disabled=no",
                    f"/ip dhcp-server network add address={network.with_prefixlen} gateway={gateway} dns-server=8.8.8.8"
                ])
                print(f"✅ DHCP server activated on {interfaceHost}", flush=True)
            else:
                print("❌ Network range too small, failed to create IP pool", flush=True)

        # PPPoE Server
        print(f"🔄 Enabling PPPoE server on {interfacePPPoE}...", flush=True)
        net_connect.send_config_set([f"/interface pppoe-server server add service-name=pppoe_server interface={interfacePPPoE} disabled=no"])
        print(f"✅ PPPoE server activated on {interfacePPPoE}", flush=True)

        # User update
        print("🔄 Updating admin username & password...", flush=True)
        if newUser != "admin" or newPass != "":
            net_connect.send_config_set([f"/user set [find name=admin] name={newUser} password={newPass}"])
            print("✅ Username & password updated", flush=True)
        else:
            print("ℹ️ Username/password unchanged (still default)", flush=True)

        print("🎉 Auto configuration finished successfully!", flush=True)

    except Exception as e:
        raise Exception(f"Error: {e}")

