import socket
import threading
from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from pyskiplist import SkipList

class ClientList:
    def __init__(self):
        self.client_dict = {}
        self.ip_dict = {}
        self.server_dict = {}
        self.sl = SkipList()

    def get_server_dict(self):
        return self.server_dict

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

def handle_tcp(data, rosie, ClientList):
    if data.startswith("NEW"):
        rosie += 10             #spawn at the next x value
        clientID = data[4:7]
        ClientList.insert_client(client_x=rosie, client_id=clientID, client_ip=data[8:])       #insert at x, with id and ip from the login server
        client_server = ClientList.get_server(clientID)
        ClientList.get_server_dict()[clientID] = client_server
        #now need to send to gameserver about the new client?
        return rosie

def handle_udp(data, ClientList, servers_list, udp_socket):
    if data.startswith("g"):                #if data is intended for the gameserver
        indi = data.find("&")
        clientID = data[indi+1:indi+4]          #find ID by msg
        clientServer = ClientList.get_server(clientID)
        ClientList.get_server_dict[clientID] = clientServer         #update the server dict every time a client sends a request - the server dict contains information about clients that was true when the client last sent a request
        udp_socket.sendto(data, servers_list[clientServer])          #send msg to the matching gameserver
        return

    if data.startswith("l"):                #if data is intended for login server
        udp_socket.sendto(data, servers_list['login'])                                  #send msg to the login server
        return

    if data.startswith("c"):                #if data is intended for clients
        indi = data.find("&")
        serverID = data[indi+1]             #1, 2, 3 or 4
        for clientID in ClientList.get_server_dict():
            if ClientList.get_server_dict()[clientID] == serverID:          #if the client belongs to the relevant server
                udp_socket.sendto(data, ClientList.get_ip_dict()[clientID])             #then send the msg to the client
        return

    if data.startswith("REM"):
        clientID = data[4:7]
        serverID = ClientList.get_server(clientID)
        ClientList.remove_client(clientID)
        del ClientList.get_server_dict()[clientID]
        udp_socket.sendto(data, servers_list['login'])
        #if type is death, send msg death, if type is helicopter, send type heli, .........
        #NEEDS TO BE FILLED OUT!!!!!!!

# Function to handle TCP connections
def tcp_server(host, port, ClientList, servers_list):
    rosie = 0
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
        rosie = handle_tcp(data, rosie, ClientList)

# Function to handle UDP connections
def udp_server(host, port, ClientList, servers_list):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print("UDP Server listening on " + str(host) + ", " + str(port))

    while True:
        data, client_address = udp_socket.recvfrom(1024)
        print("New UDP message from " + str(client_address) + ": " + data.decode())
        handle_udp(data.decode(), ClientList, servers_list, udp_socket)

def main():

    tcp_host = '127.0.0.1'
    tcp_port = 8888

    udp_host = '127.0.0.1'
    udp_port = 9999

    servers_dict = {1:('127.0.0.1', 8888), 2:('127.0.0.1', 8888), 3:('127.0.0.1', 8888), 4:('127.0.0.1', 8888), 'login':('127.0.0.1', 8888)}

    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=tcp_server, args=(tcp_host, tcp_port, ClientList, servers_dict))
    tcp_thread.start()

    # Start UDP server in a separate thread
    udp_thread = threading.Thread(target=udp_server, args=(udp_host, udp_port, ClientList, servers_dict))
    udp_thread.start()

if __name__ == "__main__":
    main()
