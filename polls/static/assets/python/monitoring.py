from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiCommunicationError, RouterOsApiConnectionError
from pprint import pprint
import json


def get_mikrotik_info():
    # Konfigurasi Mikrotik
    host = '192.168.0.141'
    username = 'manik'
    password = 'manik'
    port = 8728  # default API port RouterOS (non-ssl)

    try:
        api_pool = RouterOsApiPool(
            host,
            username,
            password,
            port=port,
            plaintext_login=True
        )
        
        api = api_pool.get_api()

        # Contoh ambil resource
        resource = api.get_resource('/system/resource')
        system_info = resource.get()[0]
        
        interfaces = api.get_resource('/interface')
        data = interfaces.get()

        cpu_freq = int(system_info["cpu-frequency"])
        if cpu_freq >= 1000:
            readable_freq = cpu_freq / 1000
        else:
            readable_freq = cpu_freq

        interface_data = []
        
        
        
 
        free_memory = int(system_info['free-memory']) / 1_000_000 
        total_memory = int(system_info['total-memory']) / 1_000_000  
        
        
    

        for iface in data:
            
            rx_byte = int(iface.get('rx-byte', 0))
            tx_byte = int(iface.get('tx-byte', 0))
            
            rx_mbps = round((rx_byte * 8) / 1_000_000, 2),
            tx_mbps = round((tx_byte * 8) / 1_000_000, 2),
            
            interface_data.append({
                'name': iface['name'],
                # 'rx_byte': iface.get('rx-byte', 0),
                # 'tx_byte': iface.get('tx-byte', 0),
                'rx_mbps': rx_mbps,
                'tx_mbps': tx_mbps
        })

        api_pool.disconnect()

        return {
            'uptime': system_info['uptime'],
            'cpu_load': system_info['cpu-load'],
            'cpu_freq': round( readable_freq,2),
            'free_memory': round(free_memory, 2),
            'total_memory': round(total_memory, 2),
            'version': system_info['version'],
            'board_name': system_info['board-name'],
            'interface': interface_data,
        }
        
        # return system_info;

    except (RouterOsApiCommunicationError, RouterOsApiConnectionError) as e:
        pprint(f"Error: {e}")
        return None
    
    
if __name__ == '__main__':
    result = get_mikrotik_info()
    print(json.dumps(result, indent=3))
   