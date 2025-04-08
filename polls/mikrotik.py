# mikrotik_utils.py
from routeros_api import RouterOsApiPool

def get_mikrotik_info(host, username, password, port=8728):
    try:
        api_pool = RouterOsApiPool(
            host,
            username,
            password,
            port=port,
            plaintext_login=True
        )
        api = api_pool.get_api()
        resource = api.get_resource('/system/resource')
        system_info = resource.get()[0]

        cpu_freq = int(system_info["cpu-frequency"])
        readable_freq = cpu_freq / 1000 if cpu_freq >= 1000 else cpu_freq

        free_memory = int(system_info['free-memory']) / 1_000_000 
        total_memory = int(system_info['total-memory']) / 1_000_000

        interfaces = api.get_resource('/interface')
        data = interfaces.get()  

        interface_data = []

        for iface in data:
            
            rx_byte = int(iface.get('rx-byte', 0))
            tx_byte = int(iface.get('tx-byte', 0))
            
            rx_mbps = round((rx_byte * 8) / 1_000_000, 2),
            tx_mbps = round((tx_byte * 8) / 1_000_000, 2),
            
            interface_data.append({
                'name': iface['name'],
                'rx_mbps': rx_mbps,
                'tx_mbps': tx_mbps
        })

        api_pool.disconnect()

        return {
            'uptime': system_info['uptime'],
            'cpu' : system_info['cpu'],
            'cpu_count' : system_info['cpu-count'],
            'cpu_load': system_info['cpu-load'],
            'cpu_freq': round(readable_freq, 2),
            'free_memory': round(free_memory, 2),
            'total_memory': round(total_memory, 2),
            'version': system_info['version'],
            'board_name': system_info['board-name'],
            'interface': interface_data,
        }
    except Exception as e:
        return {'error': str(e)}
