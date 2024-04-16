from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
import socket
from bson.objectid import ObjectId
import LobbyUI

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"

db_client = MongoClient(connection_string)

login_serverDB = db_client.login_server
collections = login_serverDB.list_collection_names()
users_collection = login_serverDB.users


def update_user_address(client_ip, client_port, user_id):
    _id = ObjectId(user_id)

    updates = {
        "$set": {"ip": client_ip},
        "$set": {"port": client_port}
    }
    users_collection.update_one({"_id": _id}, updates)


def insert_new_user(username, user_password, client_ip, client_port):
    user_document = {
        "name": username,
        "password": user_password,
        "ip": client_ip,
        "port": client_port,
        "money": 0,
        "ak-47": 0,
        "m4": 0,
        "awp": 0,
        "mp5": 0,
        "medkit": 0,
        "bandage": 0,
        "speed_potion": 0,
        "leaping_potion": 0
    }

    users_collection.insert_one(user_document)


def init_lobby(client_socket, user_document):
    ak = user_document["ak-47"]
    m4 = user_document["m4"]
    awp = user_document["awp"]
    mp5 = user_document["mp5"]
    med_kit = user_document["medkit"]
    bandage = user_document["bandage"]
    s_potion = user_document["speed_potion"]
    l_potion = user_document["leaping_potion"]
    money = user_document["money"]

    response = f"{ak}&{m4}&{awp}&{mp5}&{med_kit}&{bandage}&{s_potion}&{l_potion}&{money}"
    client_socket.send(response.encode())


def login(client_socket, client_address, data):
    username, passwrd = data.split("&")
    user_document = users_collection.find_one({"name": username, "password": passwrd})
    if user_document:
        ip, port = client_address
        update_user_address(ip, port, user_document["_id"])
        print("sending valid")
        client_socket.send("Login_successful".encode())
        init_lobby(client_socket, user_document)
        print("VALID")

    else:
        print("sending invalid")
        client_socket.send("Login_failed".encode())
        print("NOT")


def sign_in(client_socket, client_address, data):
    username, passwrd = data.split("&")
    user_document = users_collection.find_one({"name": username})
    if user_document:
        client_socket.send(f"Taken".encode())
    else:
        ip, port = client_address
        insert_new_user(username, passwrd, ip, port)


def update_user(data, client_address):
    ip, port = client_address
    user_document = users_collection.find_one({"ip": ip, "port": port})
    _id = ObjectId(user_document["_id"])

    print(data)

    ak_count, m4_count, awp_count, mp5_count, med_kit_count, bandage_count, sp_count, lp_count = data.split('&')
    updates = {
        "$inc": {"ak-47": int(ak_count)},
        "$inc": {"m4": int(m4_count)},
        "$inc": {"awp": int(awp_count)},
        "$inc": {"mp5": int(mp5_count)},
        "$inc": {"medkit": int(med_kit_count)},
        "$inc": {"bandage": int(bandage_count)},
        "$inc": {"speed_potion": int(sp_count)},
        "$inc": {"leaping_potion": int(lp_count)}
    }
    print("bulbul")

    users_collection.update_one({"_id": _id}, updates)
    print("bulbulon")


def buy_shit(data, client_socket, client_address):
    print("buy shit")
    client_ip, client_port = client_address
    print(client_ip)
    print(client_port)
    user_document = users_collection.find_one({"ip": client_ip, "port": client_port})
    ak_count, m4_count, awp_count, mp5_count, med_kit_count, bandage_count, sp_count, lp_count = data.split('&')
    print(user_document["_id"])

    if int(ak_count) * 2700 + int(m4_count) * 3100 + int(awp_count) * 4750 + int(mp5_count) * 1500 + int(
            med_kit_count) * 1000 + int(bandage_count) * 650 + int(sp_count) * 1800 + int(lp_count) * 1200 < \
            user_document["money"]:
        update_user(data, client_address)
        client_socket.send("successful buy".encode())

    else:
        print("cheater")
        client_socket.send("CHEATER".encode())


def handle_client(client_socket, client_address):
    """
    Handle a client request by parsing the request, determining the appropriate action, and responding accordingly.
    """
    while True:
        data = client_socket.recv(1024).decode()

        print(data)

        # Parse the request data
        method, data = data.split("%")
        print(data)
        print(method)

        match method:
            case "Login":
                login(client_socket, client_address, data)
            case "Sign in":
                sign_in(client_socket, client_address, data)
            case "Buy":
                print("buy")
                buy_shit(data, client_socket, client_address)


def main():
    """
    Main function to initialize and run the server.
    """
    server_socket = socket.socket()
    server_socket.bind(("127.0.0.1", 6969))
    server_socket.listen()

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        handle_client(client_socket, client_address)


if __name__ == "__main__":
    main()
