from netmiko import ConnectHandler


def get_mikrotik_conn (host, username, password):
    device = {
        'device_type' : 'mikrotik_routeros',
        'host' : host,
        'username' : username,
        'password' : password,
    }
    return  ConnectHandler(**device)


def clear_config(host, username, password, pools=None):
    try:
        conn = get_mikrotik_conn(host, username, password)

        if pools:
            for pool_item in pools:
                command = f'/ip pool remove [find name="{pool_item}"]'
                conn.send_command(command)

        conn.disconnect()
        return True

    except Exception as e:
        raise Exception(f"Error: {e}")

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


def delete_pool(host, username, password, current_pool):
    try:
        conn = get_mikrotik_conn(host, username, password)
        command = f"/ip pool remove {current_pool}"
        output = conn.send_command(command)
        return output
    except Exception as e:
        raise Exception(f"Gagal hapus IP pool: {e}")