import math
import socket
import queue
import threading
import time
import select
from pyskiplist import SkipList
import random
from sympy import randprime

UPDATE_RATE = 10  # update the client's positions in the databases every UPDATE_RATEth movement msg from a client
SERVER_UPDATE_RATE = 10  # update the lb values every SERVER_UPDATE_RATEth msg movement msg from a client
LOOKING_DISTANCE = 20  # the max distance from which you can see other ppl
CLIENT_ID_LENGTH = 5


class ClientLister:
    def __init__(self):
        self.join_dict = {}
        self.client_dict = {}  # dict that matches ID to x pos
        self.client_dict_z = {}
        self.edges_arr = [100, 200, 300]  # arr that holds the x positions of the edges of the rectangles
        self.ip_dict = {}  # dict that matches ID to ip
        self.server_dict = {}  # dict that matches between ID and server
        self.update_dict = {}  # dict that holds the mov msgs counter for each client (and the total counter)
        self.sl = SkipList()  # ordered skip list that holds x positions with ID's as keys
        self.hellman = {}
        self.public = {}
    def get_join(self):
        return self.join_dict

    def get_public(self):
        return self.public

    def get_hellman(self):
        return self.hellman

    def get_edges_arr(self):
        return self.edges_arr

    def get_update_dict(self):
        return self.update_dict

    def get_server_dict(self):
        return self.server_dict

    def get_ip_dict(self):
        return self.ip_dict

    def get_dict(self):
        return self.client_dict

    def get_sl(self):
        return self.sl

    def get_z_dict(self):
        return self.client_dict_z

    def insert_new_client(self, client_x, client_z, client_id, client_ip):
        indi = client_ip.find(",")
        ip = client_ip[1:indi]
        bindi = client_ip.find(")")
        port = client_ip[indi + 2:bindi]
        real_addr = (ip, int(port))

        self.ip_dict[int(client_id)] = real_addr
        self.client_dict[int(client_id)] = client_x
        self.client_dict_z[int(client_id)] = client_z
        self.sl.insert(client_x, client_id)
        self.update_dict[int(client_id)] = 0  # make a new slot in the update list, init to 0

    def insert_client(self, client_x, client_z, client_id):
        self.client_dict[client_id] = client_x
        self.client_dict_z[client_id] = client_z
        self.sl.insert(client_x, client_id)

    def remove_client(self, client_id):
        client_x = self.client_dict.pop(client_id)
        gh = self.client_dict_z.pop(client_id)
        self.sl.remove(client_x)

    def update_client(self, new_x, new_z, client_id):
        self.remove_client(client_id)
        self.insert_client(new_x, new_z, client_id)

    def calc_edges(self):
        num_clients = len(self.client_dict)
        self.edges_arr[0] = self.sl[int(num_clients / 4 * 1)][0]
        self.edges_arr[1] = self.sl[int(num_clients / 4 * 2)][0]
        self.edges_arr[2] = self.sl[int(num_clients / 4 * 3)][0]

    def get_server(self, client_id):
        client_x = self.client_dict[int(client_id)]

        if client_x < self.edges_arr[0]:
            return (1, 0)  # only in first one

        if client_x < self.edges_arr[1]:
            return (2, 0)  # only in second one

        if client_x < self.edges_arr[2]:
            return (3, 0)  # only in third one

        return (4, 0)  # only in fourth one


def print_status(ClientList):
    in_first = 0
    in_second = 0
    in_third = 0
    in_fourth = 0

    '''for client_x in ClientList.get_dict().values():
        ind = sl.index(client_x)
        yas = (ind*4) // length
        if client == 0:
            in_first += 1
        elif yas == 1:
            in_second += 1
        elif yas == 2:
            in_third += 1
        else:
            in_fourth += 1

    print("in first: {}, in second: {}, in third: {}, in fourth: {}".format(in_first, in_second, in_third, in_fourth))'''


def handle_tcp(data, rosie, ClientList, servers_list, udp_socket, shared_secret):
    data = decrypt_login(data, shared_secret)

    if data.startswith("NEW"):
        dataArr = data.split('&')
        clientID = dataArr[1]
        clientIP = dataArr[2]
        ClientList.insert_new_client(client_x=0, client_z=0, client_id=clientID,
                                     client_ip=clientIP)  # insert at x, with id and ip from the login server
        ClientList.calc_edges()
        client_server = ClientList.get_server(clientID)
        ClientList.get_server_dict()[clientID] = client_server
        server_ip = servers_list[client_server[0]]

        for clientIP in ClientList.get_ip_dict().values():  # for every client:
            udp_socket.sendto(data.encode(), clientIP)

        ##server_socket = yes_dict[server_ip]
        ##data = "yes yes yes i am big i am smoll yes yes yes"                                #update yes!
        ##server_socket.send(data.encode())
        return rosie

    if data.startswith("JOIN"):
        print("Received JOIN request")
        dataArr = data.split('&')
        clientID = int(dataArr[1])
        ClientList.get_join()[clientID] = data
        #for serverIP in servers_list.values():
        #    udp_socket.sendto(data.encode(), serverIP)

def decrypt(data, ClientList):
    print("trying to decrypt: ", data)
    # Convert key to bytes (using 4 bytes and little endian byteorder)
    indi = data.split(b'&', 1)
    clientID = int(indi[0].decode('ascii', 'ignore'))
    print("while decrypting, the ID is: ")
    shared_key = ClientList.get_hellman()[ClientList.get_public()[clientID]]
    data = indi[1]
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the encrypted message and the key
    decrypted_bytes = bytes([encrypted_byte ^ key_byte for encrypted_byte, key_byte in zip(data, key_bytes)])
    # Convert the decrypted bytes back to a string
    decrypted_message = decrypted_bytes.decode('ascii', 'ignore')

    return decrypted_message

def decrypt_login(data, shared_secret):

    key_bytes = shared_secret.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the encrypted message and the key
    decrypted_bytes = bytes([encrypted_byte ^ key_byte for encrypted_byte, key_byte in zip(data, key_bytes)])
    # Convert the decrypted bytes back to a string
    decrypted_message = decrypted_bytes.decode('ascii', 'ignore')

    return decrypted_message

def handle_udp(data, ClientList, servers_list, udp_socket, addr):
        pring = data
        try:
            data = data.decode(errors = 'ignore')
            #print("Received without decrypting: ", data)
            if data.startswith("s"):        #data intended for specific client
                indi = data.split('&')
                clientID = int(indi[1])
                clientIP = ClientList.get_ip_dict()[clientID]
                precious = encrypt(data, ClientList.get_hellman()[ClientList.get_public()[clientID]])
                udp_socket.sendto(precious, clientIP)
                print(f"Sent {data}")

            if data.startswith("l"):  # if data is intended for login server
                udp_socket.sendto(data.encode(), servers_list['login'])  # send msg to the login server
                return

            if data.startswith("c"):  # if data is intended for clients
                indi = data.split("&")
                clientID = int(indi[1])
                clientX = int(ClientList.get_dict()[clientID])

                for client in ClientList.get_sl().items():  # for every client:
                    if client[0] >= clientX - LOOKING_DISTANCE:  # if the client's x is big enough to see the relevant client
                        if client[0] <= clientX + LOOKING_DISTANCE:  # and if the client's x is also small enough to see
                            precious = encrypt(data, ClientList.get_hellman()[ClientList.get_public()[clientID]])
                            udp_socket.sendto(precious, ClientList.get_ip_dict()[clientID])  # then send the client
                        else:
                            return  # if the client is big enough but not small enough, then theres no reason to continue as the list is ordered
                return

            if data.startswith("a"):  # if data is intended for all clients
                for clientID in ClientList.get_ip_dict().keys():  # for every client:
                    precious = encrypt(data, ClientList.get_hellman()[ClientList.get_public()[clientID]])
                    udp_socket.sendto(precious, ClientList.get_ip_dict()[clientID])
                return

            if data.startswith("STATE"):  # this is STATE_ACK sent from gs, as STATE_UPDATE sent from client starts with g
                dataArr = data.split('&')
                clientID = int(dataArr[1])
                clientX = float(dataArr[2])
                clientZ = float(dataArr[4])
                '''indi = data.find("&")
                clientID = int(data[indi+1:indi+CLIENT_ID_LENGTH+1])
                indi = indi+CLIENT_ID_LENGTH+1
                finale = data[indi+1:].find("&") + indi + 1
                clientX = int(data[indi : finale])'''

                if ClientList.get_update_dict()[
                    clientID] % UPDATE_RATE == 0:  # every UPDATE_RATEth move ack from a specific client, update the client list with his current values
                    ClientList.update_client(clientX, clientZ, clientID)

                if ClientList.get_update_dict()[
                    'total'] % SERVER_UPDATE_RATE == 0:  # every SERVER_UPDATE_RATEth move ack, calculate the edges again by the values currently in the client list
                    ClientList.calc_edges()

                ClientList.get_update_dict()[clientID] += 1
                ClientList.get_update_dict()['total'] += 1

                '''for serverID in servers_list.keys():
                    print("server ID: ", serverID)
                    print("server IP: ", servers_list[serverID])
                    udp_socket.sendto(data.encode(), servers_list[serverID])'''

                for client in ClientList.get_sl().items():  # for every client:
                    if client[0] >= clientX - LOOKING_DISTANCE:  # if the client's x is big enough to see the relevant client
                        if client[0] <= clientX + LOOKING_DISTANCE:  # and if the client's x is also small enough to see
                            if ClientList.get_z_dict()[client[1]] >= clientZ - LOOKING_DISTANCE:
                                if ClientList.get_z_dict()[client[1]] <= clientZ + LOOKING_DISTANCE:
                                    precious = encrypt(data, ClientList.get_hellman()[ClientList.get_public()[clientID]])
                                    udp_socket.sendto(precious,
                                                      ClientList.get_ip_dict()[int(client[1])])  # then send the client
                                else:
                                    return  # if the client is big enough but not small enough, then theres no reason to continue as the list is ordered
                return

            data = decrypt(pring, ClientList)
            #print("Received with decrypting: ", data)

            if data.startswith("HI&"):
                print("Received HI MSG: ", data)
                indi = data.split('&')
                clientID = int(indi[1])
                print("Client ID is: ", clientID)
                clientIP = f'({addr[0]}, {addr[1]})'
                print("Client IP is: ",clientIP)
                print("yaya")
                bata = ClientList.get_join()[clientID]
                for serverIP in servers_list.values():
                    udp_socket.sendto(bata.encode(), serverIP)
                ClientList.get_ip_dict()[clientID] = clientIP
                ClientList.insert_new_client(client_x=0, client_z=0, client_id=clientID, client_ip=clientIP)  # insert at x, with id and ip from the login server
                print("Calculating edges")
                ClientList.calc_edges()
                client_server = ClientList.get_server(clientID)
                print("Client server is: ", client_server)
                ClientList.get_server_dict()[clientID] = client_server
                serverIP = servers_list[client_server[0]]
                udp_socket.sendto(data.encode(), serverIP)
                print(f"Sent HI msg: {data} to {serverIP}")
                return

            if data.startswith("z"):
                indi = data.split('&')
                clientID = indi[1]
                for serverID in servers_list.keys():
                    print("server ID: ", serverID)
                    print("server IP: ", servers_list[serverID])
                    udp_socket.sendto(data.encode(), servers_list[serverID])

            if data.startswith("gHELD"):
                print("REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                indi = data.split('&')
                clientID = indi[1]
                for serverID in servers_list.keys():
                    print("server ID: ", serverID)
                    print("server IP: ", servers_list[serverID])
                    udp_socket.sendto(data.encode(), servers_list[serverID])

            if data.startswith("g"):  # if data is intended for the gameserver
                indi = data.split('&')
                clientID = int(indi[1])  # find ID by msg
                #print(f"kakaikakikaki{clientID}")
                ClientList.get_server_dict()[clientID] = ClientList.get_server(clientID)
                clientServer = ClientList.get_server_dict()[clientID]
                udp_socket.sendto((data).encode(), servers_list[clientServer[0]])  # send msg to the main gameserver
                ##if clientServer[1] != 0:
                ##    udp_socket.sendto(('0' + data).encode(), servers_list[clientServer[1]])    #send msg to the secondary gameserver
                return

            if data.startswith("l"):  # if data is intended for login server
                udp_socket.sendto(data.encode(), servers_list['login'])  # send msg to the login server
                return

            if data.startswith("DISCONNECT"):
                indi = data.split("&")
                clientID = int(indi[1])
                print("Disconnecting: ", clientID)
                ClientList.remove_client(clientID)
                del ClientList.get_server_dict()[clientID]
                public = ClientList.get_public()[clientID]
                del ClientList.get_hellman()[public]
                del ClientList.get_public()[clientID]
                del ClientList.get_join()[clientID]
                #udp_socket.sendto(data.encode(), servers_list['login'])
                #for clientIP in ClientList.get_ip_dict().values():
                #    udp_socket.sendto(data.encode(), clientIP)
                return

            print("default")

            #indi = data.find("&")
            #clientID = int(data[indi + 1:indi + CLIENT_ID_LENGTH + 1])  # find ID by msg
            #ClientList.get_server_dict()[clientID] = ClientList.get_server(clientID)
            #clientServer = ClientList.get_server_dict()[clientID]
            #udp_socket.sendto((data).encode(), servers_list[clientServer[0]])  # send msg to the main gameserver
            ##if clientServer[1] != 0:
            ##    udp_socket.sendto(('0' + data).encode(), servers_list[clientServer[1]])    #send msg to the secondary gameserver
            return
        except Exception as e:
            print("error: ", e)

# Function to handle multiple TCP connections
def tcp_server(host, port, ClientList, servers_list, udp_socket):
    rosie = 0
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen()
    print("TCP Server listening on " + str(host) + ", " + str(port))
    login_socket, login_address = tcp_socket.accept()

    prime = gen_prime()
    base = gen_primitive_root(prime)  # You can choose any suitable base, typically a primitive root modulo prime

    # Send prime and base to the client
    login_socket.send(str(prime).encode())
    login_socket.send(str(base).encode())

    # Generate server's private key
    private_key_server = random.randint(1, prime - 1)

    # Calculate public key to send to the client
    public_key_server = pow(base, private_key_server, prime)
    login_socket.send(str(public_key_server).encode())

    # Receive client's public key
    data = (login_socket.recv(1024).decode())
    public_key_client = int(data)

    # Calculate shared secret
    shared_secret = pow(public_key_client, private_key_server, prime)
    print("shared secret is: ", shared_secret)
    #ClientList.get_public()[client_id] = public_key_client

    while True:
        data = login_socket.recv(9192)
        if not data:
            break
        print(f"Received: {data}")
        rosie = handle_tcp(data=data, rosie=rosie, ClientList=ClientList, servers_list=servers_list,
                           udp_socket=udp_socket, shared_secret=shared_secret)

    '''inputs = [tcp_socket]  # List of input sockets to monitor

    yes_dict = {}

    while True:
        # Wait for one of the sockets to become ready for reading
        readable, _, _ = select.select(inputs, [], [])

        for ready_socket in readable:
            if ready_socket is tcp_socket:          #if the ready socket is the main socket, then theres a new connection pending
                client_socket, client_address = tcp_socket.accept()
                print(f"Connected with {client_address}")
                inputs.append(client_socket)                # Add client socket to the list of monitored inputs
                yes_dict[client_address] = client_socket            #add to dict

            else:               # Handle data from an existing client connection
                data = ready_socket.recv(9192)

                if data:
                    print(f"Received data from {ready_socket.getpeername()}: {data.decode()}")
                    # Process data using the handle_func function
                    rosie = handle_tcp(data=data.decode(), rosie=rosie, ClientList=ClientList, yes_dict=yes_dict, servers_list=servers_list, udp_socket=udp_socket)

                else:                   #if !data, then the connection was closed
                    print(f"Connection with {ready_socket.getpeername()} closed")
                    ready_socket.close()
                    inputs.remove(ready_socket)  # Remove closed socket from the list of monitored inputs'''


# Function to handle UDP connections
def udp_server(host, port, ClientList, servers_list, udp_socket):
    print("UDP Server listening on " + str(host) + ", " + str(port))

    message_queue = queue.Queue()

    def process_messages():
        #udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                data, client_address = message_queue.get(timeout=1)
                handle_udp(data, ClientList, servers_list, udp_socket, client_address)
                #print("Handling UDP message from " + str(client_address) + ": " + message)
                # Call your handle_udp function here with appropriate arguments
                # handle_udp(message, ClientList, servers_list, udp_socket, client_address)
            except queue.Empty:
                pass

    pool_size = 15
    threads = []
    for _ in range(pool_size):
        thread = threading.Thread(target=process_messages)
        thread.start()
        threads.append(thread)

    while True:
        try:
            data, client_address = udp_socket.recvfrom(9192)
            if data:
                message_queue.put((data, client_address))
        except Exception as e:
            print("error: ", e)

def gen_prime():
    # Function to generate a large prime number
    return randprime(2 ** 1023, 2 ** 1024 - 1)


def gen_primitive_root(p):
    while True:
        g = random.randint(2, p - 1)
        if pow(g, (p - 1) // 2, p) != 1 and pow(g, 2, p) != 1:
            return g


def server_program(ClientList, kaki, kadki):
    host = '0.0.0.0'
    port = 1010

    prime = gen_prime()
    base = gen_primitive_root(prime)  # You can choose any suitable base, typically a primitive root modulo prime

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    while(True):
        connection, address = server_socket.accept()

        # Send prime and base to the client
        connection.send(str(prime).encode())
        connection.send(str(base).encode())

        # Generate server's private key
        private_key_server = random.randint(1, prime - 1)

        # Calculate public key to send to the client
        public_key_server = pow(base, private_key_server, prime)
        connection.send(str(public_key_server).encode())

        # Receive client's public key
        data = (connection.recv(1024).decode())
        public_key_client = int(data.split('&')[0])
        client_id = int(data.split('&')[1])
        print("client id is: ", client_id)

        # Calculate shared secret
        shared_secret = pow(public_key_client, private_key_server, prime)
        print("shared secret is: ", shared_secret)
        connection.close()
        ClientList.get_hellman()[public_key_client] = shared_secret
        ClientList.get_public()[client_id] = public_key_client

def encrypt(data, shared_key):
    # Convert message and key to byte arrays
    message_bytes = data.encode('ascii', 'ignore')
    key_bytes = shared_key.to_bytes(1024, byteorder = 'little')

    # Perform XOR operation between each byte of the message and the key
    encrypted_bytes = bytes([message_byte ^ key_byte for message_byte, key_byte in zip(message_bytes, key_bytes)])
    print(encrypted_bytes)
    return encrypted_bytes

def main():
    tcp_host = '127.0.0.1'
    tcp_port = 8888

    udp_host = '127.0.0.1'
    udp_port = 9999

    servers_dict = {1: ('127.0.0.1', 12341), 2: ('127.0.0.1', 12342), 3: ('127.0.0.1', 12343), 4: ('127.0.0.1', 12344),
                    'login': ('127.0.0.1', 12345)}

    ClientList = ClientLister()

    ClientList.get_update_dict()['total'] = 0

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((udp_host, udp_port))

    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=tcp_server, args=(tcp_host, tcp_port, ClientList, servers_dict, udp_socket))
    tcp_thread.start()

    # Start UDP server in a separate thread
    udp_thread = threading.Thread(target=udp_server, args=(udp_host, udp_port, ClientList, servers_dict, udp_socket))
    udp_thread.start()

    diffie = threading.Thread(target=server_program, args=(ClientList, servers_dict, udp_socket))
    diffie.start()

if __name__ == "__main__":
    main()
