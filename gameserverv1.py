import socket

# change this to multithreading later on
BROAD_ADDR = {}
IP = "127.0.0.1"
PORT = 5555


def reqhandler(data, server_socket) :
    for key in BROAD_ADDR :
        server_socket.sendto(data.encode(), BROAD_ADDR[key])  # broadcasts


def main() :
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    while True :
        (data, address) = server_socket.recvfrom(1024)
        BROAD_ADDR[data.decode().split()[0]] = address
        reqhandler(data.decode(), server_socket)

    server_socket.close()


if __name__ == "__main__" :
    main()
