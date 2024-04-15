import socket
import threading
LOAD_BALANCER_UDP_ADDR = ('127.0.0.1', 9999)
def handle_udp():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('localhost', 8989))
    print("UDP Server listening on localhost:8989")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Received UDP message from {addr}: {data.decode()}")

        # Respond via TCP
        tcp_response(data, addr)

def tcp_response(data, udp_addr):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(('localhost', 8888))

    # Send UDP data via TCP
    tcp_socket.sendall(data)

    # Receive response from TCP server
    response = tcp_socket.recv(1024)
    print(f"Received TCP response: {response.decode()}")

    tcp_socket.close()

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect(('localhost', 8888))

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('localhost', 8989))

while True:
    print("UDP Server listening on localhost:8989")
    data, addr = udp_socket.recvfrom(1024)
    print(f"Received UDP message from {addr}: {data.decode()}")
    tcp_socket.sendall(data)