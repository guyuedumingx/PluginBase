import socket

def get_local_ip():
    try:
        # 获取本机主机名
        host_name = socket.gethostname()
        # 通过主机名获取本机 IP 地址列表
        ip_list = socket.gethostbyname_ex(host_name)[2]
        # 从 IP 地址列表中选择非回环地址（127.0.0.1）的地址
        local_ip = next((ip for ip in ip_list if not ip.startswith("127.")), None)

        return local_ip
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    local_ip = get_local_ip()

    if local_ip:
        print(f"Your local IP address in the LAN is: {local_ip}")
    else:
        print("Unable to retrieve local IP address.")
