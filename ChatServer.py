import socket


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    clients = set()

    try:
        print(f"Server started at {host}:{port}")
        while True:
            msg, addr = server_socket.recvfrom(1024)
            if addr not in clients:
                clients.add(addr)
                print(f"New client: {addr}")

            print(f"Received message from {addr}: {msg.decode()}")

            for client in clients:
                server_socket.sendto(msg, client)
                print(msg)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()


# Run the server
def Chat():
    start_server('127.0.0.1', 57687)