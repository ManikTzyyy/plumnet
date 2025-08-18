from django.test import TestCase
from netmiko import ConnectHandler
import traceback
# Create your tests here.



def get_mikrotik_conn (host, username, password):
    device = {
        'device_type' : 'mikrotik_routeros',
        'host' : host,
        'username' : username,
        'password' : password,
    }
    return  ConnectHandler(**device)




def test_conn():
    host = '192.168.10.1'
    user = 'admin'
    password = 'admin'  
    try : 
        conn = get_mikrotik_conn(host, user, password)
        # result = conn.is_alive()
        output = conn.send_command("/system resource print")
        conn.disconnect()
        return f"koneksi ok, Device Info:\n{output}"

    except Exception as e:
        return f"Error: {e}"
        

print(test_conn())



