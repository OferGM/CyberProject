import socket
import threading
import select
from pyskiplist import SkipList

UPDATE_RATE = 1            #update the client's positions in the databases every UPDATE_RATEth movement msg from a client
SERVER_UPDATE_RATE = 1         #update the lb values every SERVER_UPDATE_RATEth msg movement msg from a client
LOOKING_DISTANCE = 30           #the max distance from which you can see other ppl
CLIENT_ID_LENGTH = 3

class ClientLister:
    def __init__(self):
        self.client_dict = {}                       #dict that matches ID to x pos
        self.edges_arr = [100, 200, 300]            #arr that holds the x positions of the edges of the rectangles
        self.ip_dict = {}                           #dict that matches ID to ip
        self.server_dict = {}                       #dict that matches between ID and server
        self.update_dict = {}                       #dict that holds the mov msgs counter for each client (and the total counter)
        self.sl = SkipList()                        #ordered skip list that holds x positions with ID's as keys

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

    def insert_new_client(self, client_x, client_id, client_ip):
        indi = client_ip.find(",")
        ip = client_ip[1:indi]
        bindi = client_ip.find(")")
        port = client_ip[indi+2:bindi]
        real_addr = (ip, int(port))

        self.ip_dict[client_id] = real_addr
        self.client_dict[client_id] = client_x
        self.sl.insert(client_x, client_id)
        self.update_dict[client_id] = 0                #make a new slot in the update list, init to 0

    def insert_client(self, client_x, client_id):
        self.client_dict[client_id] = client_x
        self.sl.insert(client_x, client_id)

    def remove_client(self, client_id):
        client_x = self.client_dict.pop(client_id)
        self.sl.remove(client_x)

    def update_client(self, new_x, client_id):
        self.remove_client(client_id)
        self.insert_client(new_x, client_id)

    def calc_edges(self):
        num_clients = len(self.client_dict)
        self.edges_arr[0] = self.sl[num_clients//4*1][0]
        self.edges_arr[1] = self.sl[num_clients//4*2][0]
        self.edges_arr[2] = self.sl[num_clients//4*3][0]

    def get_server(self, client_id):
        client_x = self.client_dict[client_id]

        if client_x < self.edges_arr[0]:
            if client_x > self.edges_arr[0] - LOOKING_DISTANCE:       #in leftomost rect, but also in the second one
                return (1, 2)
            return (1, 0)           #only in first one

        if client_x < self.edges_arr[1]:
            if client_x < self.edges_arr[0] + LOOKING_DISTANCE:       #in the second rect, but also in the first one
                return (2, 1)
            if client_x > self.edges_arr[1] - LOOKING_DISTANCE:       #in the second rect, but also in the third one
                return (2, 3)
            return (2, 0)           #only in second one

        if client_x < self.edges_arr[2]:
            if client_x < self.edges_arr[1] + LOOKING_DISTANCE:       #in the third rect, but also in the second one
                return (3, 2)
            if client_x > self.edges_arr[2] - LOOKING_DISTANCE:       #in the third rect, but also in the
                return (3, 4)
            return (3, 0)          #only in third one

        if client_x < self.edges_arr[2] + LOOKING_DISTANCE:           #in the fourth rect, but also in the third one
            return (4, 3)
        return (4, 0)              #only in fourth one


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

def handle_tcp(data, rosie, ClientList, yes_dict, servers_list):
    if data.startswith("s"):                        #intended for one specific client, not all of them
        indi = data.find("&")
        clientID = data[(indi+1):(indi+4)]
        clientIP = ClientList.get_ip_dict()[clientID]           #address of client
        client_socket = yes_dict[clientIP]
        client_socket.send(data.encode())

    if data.startswith("NEW"):
        rosie += 10             #spawn at the next x value, NEEDS UPDATE!
        clientID = int(data[4:4+CLIENT_ID_LENGTH])
        ClientList.insert_new_client(client_x=rosie, client_id=clientID, client_ip=str(data[8:]))       #insert at x, with id and ip from the login server
        client_server = ClientList.get_server(clientID)
        ClientList.get_server_dict()[clientID] = client_server
        print("client server is: " + str(client_server))
        server_ip = servers_list[client_server[0]]
        ##server_socket = yes_dict[server_ip]
        ##data = "yes yes yes i am big i am smoll yes yes yes"                                #update yes!
        ##server_socket.send(data.encode())
        return rosie

def handle_udp(data, ClientList, servers_list, udp_socket):
    if data.startswith("g"):                #if data is intended for the gameserver
        indi = data.find("&")
        clientID = int(data[indi+1:indi+CLIENT_ID_LENGTH+1])          #find ID by msg
        ClientList.get_server_dict()[clientID] = ClientList.get_server(clientID)
        clientServer = ClientList.get_server_dict()[clientID]
        udp_socket.sendto((data).encode(), servers_list[clientServer[0]])  # send msg to the main gameserver
        ##if clientServer[1] != 0:
        ##    udp_socket.sendto(('0' + data).encode(), servers_list[clientServer[1]])    #send msg to the secondary gameserver
        return

    if data.startswith("l"):                #if data is intended for login server
        udp_socket.sendto(data.encode(), servers_list['login'])                                  #send msg to the login server
        return

    if data.startswith("c"):                #if data is intended for clients
        indi = data.find("&")
        clientID = int(data[indi+1:indi+CLIENT_ID_LENGTH+1])
        indi = data[indi+1:].find("&")
        clientX = int(ClientList.get_dict()[clientID])

        for client in ClientList.get_sl().items():                  #for every client:
            if client[0] >= clientX - LOOKING_DISTANCE:                     #if the client's x is big enough to see the relevant client
                if client[0] <= clientX + LOOKING_DISTANCE:                         #and if the client's x is also small enough to see
                    udp_socket.sendto((data).encode(), ClientList.get_ip_dict()[clientID])              #then send the client
                else:
                    return                  #if the client is big enough but not small enough, then theres no reason to continue as the list is ordered
        return

    if data.startswith("a"):                #if data is intended for all clients
        for clientIP in ClientList.get_ip_dict().values():                  #for every client:
            udp_socket.sendto((data).encode(), clientIP)
        return

    if data.startswith("STATE"):                  #this is STATE_ACK sent from gs, as STATE_UPDATE sent from client starts with g
        print(ClientList.get_ip_dict().items())
        indi = data.find("&")
        clientID = int(data[indi+1:indi+CLIENT_ID_LENGTH+1])
        indi = indi+CLIENT_ID_LENGTH+1
        finale = data[indi:].find("&")
        clientX = int(data[indi + 1 : indi+3])

        if ClientList.get_update_dict()[clientID] % UPDATE_RATE == 0:           #every UPDATE_RATEth move ack from a specific client, update the client list with his current values
            ClientList.update_client(clientX, clientID)

        if ClientList.get_update_dict()['total'] % SERVER_UPDATE_RATE == 0:     #every SERVER_UPDATE_RATEth move ack, calculate the edges again by the values currently in the client list
            ClientList.calc_edges()

        ClientList.get_update_dict()[clientID] += 1
        ClientList.get_update_dict()['total'] += 1

        ClientList.get_server_dict()[clientID] = ClientList.get_server(clientID)
        clientServer = ClientList.get_server_dict()[clientID]
        udp_socket.sendto(data.encode(), servers_list[clientServer[0]])  #send msg to the main gameserver

        for client in ClientList.get_sl().items():                  #for every client:
            if client[0] >= clientX - LOOKING_DISTANCE:                     #if the client's x is big enough to see the relevant client
                if client[0] <= clientX + LOOKING_DISTANCE:                         #and if the client's x is also small enough to see
                    print(ClientList.get_ip_dict().items())
                    udp_socket.sendto(data.encode(), ClientList.get_ip_dict()[clientID])              #then send the client
                else:
                    return                  #if the client is big enough but not small enough, then theres no reason to continue as the list is ordered
        return

    if data.startswith("REM"):
        indi = data.find("&")
        clientID = int(data[indi+1:indi+CLIENT_ID_LENGTH+1])
        ClientList.remove_client(clientID)
        del ClientList.get_server_dict()[clientID]
        print_status(ClientList.get_sl(), ClientList.get_dict())
        udp_socket.sendto(data.encode(), servers_list['login'])
        for clientIP in ClientList.get_ip_dict().values():
            udp_socket.sendto(data.encode(), clientIP)
        return

# Function to handle multiple TCP connections
def tcp_server(host, port, ClientList, servers_list):
    rosie = 0
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(100)
    print("TCP Server listening on " + str(host) + ", " + str(port))
    inputs = [tcp_socket]  # List of input sockets to monitor

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
                data = ready_socket.recv(1024)

                if data:
                    print(f"Received data from {ready_socket.getpeername()}: {data.decode()}")
                    # Process data using the handle_func function
                    handle_tcp(data=data.decode(), rosie=rosie, ClientList=ClientList, yes_dict=yes_dict, servers_list=servers_list)

                else:                   #if !data, then the connection was closed
                    print(f"Connection with {ready_socket.getpeername()} closed")
                    ready_socket.close()
                    inputs.remove(ready_socket)  # Remove closed socket from the list of monitored inputs

# Function to handle UDP connections
def udp_server(host, port, ClientList, servers_list):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print("UDP Server listening on " + str(host) + ", " + str(port))

    while True:
        data, client_address = udp_socket.recvfrom(1024)
        if data:
            print("New UDP message from " + str(client_address) + ": " + data.decode())
            handle_udp(data.decode(), ClientList, servers_list, udp_socket)

def main():

    tcp_host = '127.0.0.1'
    tcp_port = 8888

    udp_host = '127.0.0.1'
    udp_port = 9999

    servers_dict = {1:('127.0.0.1', 8888), 2:('127.0.0.1', 8888), 3:('127.0.0.1', 8888), 4:('127.0.0.1', 8888), 'login':('127.0.0.1', 8888)}

    ClientList = ClientLister()

    ClientList.get_update_dict()['total'] = 0

    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=tcp_server, args=(tcp_host, tcp_port, ClientList, servers_dict))
    tcp_thread.start()

    # Start UDP server in a separate thread
    udp_thread = threading.Thread(target=udp_server, args=(udp_host, udp_port, ClientList, servers_dict))
    udp_thread.start()

if __name__ == "__main__":
    main()
