import socket
import struct

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def is_local_ip(ip):
    # Check if the IP is in the local network range
    ip_parts = list(map(int, ip.split('.')))
    return ip_parts[0] == 10 or (ip_parts[0] == 172 and 16 <= ip_parts[1] <= 31) or (ip_parts[0] == 192 and ip_parts[1] == 168)

def allow_access(ip):
    return is_local_ip(ip)

def get_client_ip(request):
    return request.remote_addr
