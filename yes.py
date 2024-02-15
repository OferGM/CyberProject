import socket
import threading
from pyskiplist import SkipList

class ClientList:
    def __init__(self):
        self.client_dict = {}
        self.ip_dict = {}
        self.sl = SkipList()

    def get_ip_dict(self):
        return self.ip_dict

    def get_dict(self):
        return self.client_dict

    def get_sl(self):
        return self.sl

    def insert_client(self, client_x, client_id, client_ip):
        self.ip_dict[client_id] = client_ip
        self.client_dict[client_id] = client_x
        self.sl.insert(client_x, client_id)

    def insert_client(self, client_x, client_id):
        self.client_dict[client_id] = client_x
        self.sl.insert(client_x, client_id)

    def remove_client(self, client_id):
        del self.ip_dict[client_id]
        client_x = self.client_dict.pop(client_id)
        self.sl.remove(client_x)

    def update_client(self, new_x, client_id):
        self.remove_client(client_id)
        self.insert_client(new_x, client_id)

    def get_server(self, client_id):
        ind = self.sl.index(self.client_dict[client_id])
        length = len(self.client_dict)
        return (ind*4) // length

def print_status(sl, _dict):
    in_first = 0
    in_second = 0
    in_third = 0
    in_fourth = 0
    length = len(_dict)

    for client_x in _dict.values():
        ind = sl.index(client_x)
        yas = (ind*4) // length
        if yas == 0:
            in_first += 1
        elif yas == 1:
            in_second += 1
        elif yas == 2:
            in_third += 1
        else:
            in_fourth += 1

    print("in first: {}, in second: {}, in third: {}, in fourth: {}".format(in_first, in_second, in_third, in_fourth))

def handle_tcp(data):
    pass

def handle_udp(data):
    pass

# Function to handle TCP connections
def tcp_server(host, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen()
    print("TCP Server listening on " + str(host) + ", " + str(port))
    client_socket, client_address = tcp_socket.accept()
    print("New TCP connection from " + client_address)
    ##if client_address != login_ip
    ##  break connection

    while True:
        data = client_socket.recv(1024).decode()
        handle_tcp(data)

# Function to handle UDP connections
def udp_server(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print("UDP Server listening on " + str(host) + ", " + str(port))

    while True:
        data, client_address = udp_socket.recvfrom(1024)
        print("New UDP message from " + client_address + ": " + data.decode())
        handle_udp(data)

def main():
    tcp_host = '127.0.0.1'
    tcp_port = 8888

    udp_host = '127.0.0.1'
    udp_port = 9999

    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=tcp_server, args=(tcp_host, tcp_port))
    tcp_thread.start()

    # Start UDP server in a separate thread
    udp_thread = threading.Thread(target=udp_server, args=(udp_host, udp_port))
    udp_thread.start()

if __name__ == "__main__":
    main()
