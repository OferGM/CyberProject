from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
import socket
from bson.objectid import ObjectId
import threading

lb_socket = socket.socket()
lb_socket.connect(("127.0.0.1", 8888))

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"

db_client = MongoClient(connection_string)

login_serverDB = db_client.login_server
collections = login_serverDB.list_collection_names()
users_collection = login_serverDB.users


def change_connection_status(client_address, bool_var):
    ip, port = client_address
    user_document = users_collection.find_one({"ip": ip, "port": port})
    _id = ObjectId(user_document["_id"])
    update = {"$set": {"connected": bool_var}}
    users_collection.update_one({"_id": _id}, update)



#send ip, port when join, lb does nothing with id, client join first than server send
#def disconnect()

def update_user_address(client_ip, client_port, user_id):
    _id = ObjectId(user_id)

    updates = {
        "$set": {"ip": client_ip,
                 "port": client_port}
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
        "leaping_potion": 0,
        "connected": True
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
    print("Current state: ", response)
    client_socket.send(response.encode())


def login(client_socket, client_address, data):
    username, passwrd = data.split("&")
    user_document = users_collection.find_one({"name": username, "password": passwrd})
    if user_document:
        print("User Found")
        if not user_document["connected"]:
            ip, port = client_address
            update_user_address(ip, port, user_document["_id"])

            print("Login successful")
            client_socket.send("Login_successful".encode())

            change_connection_status(client_address, True)
            print(f"{client_address} is now logged in")

            init_lobby(client_socket, user_document)

        else:
            print("User already connected. Failed to login")
            client_socket.send("User_already_connected".encode())

    else:
        print("User not found. Failed to login")
        client_socket.send("Login_failed".encode())


def sign_in(client_socket, client_address, data):
    username, passwrd = data.split("&")
    user_document = users_collection.find_one({"name": username})
    if user_document:
        print("Username taken. Failed to sign up (in)")
        client_socket.send("Taken".encode())
    else:
        ip, port = client_address
        insert_new_user(username, passwrd, ip, port)
        print("Sign in successful")
        client_socket.send("Sign_in_successful".encode())
        user_document = users_collection.find_one({"name": username})
        change_connection_status(client_address, True)
        print(f"{client_address} is now logged into the game")
        init_lobby(client_socket, user_document)


def update_user(data, client_address, buy_sum):
    ip, port = client_address
    user_document = users_collection.find_one({"ip": ip, "port": port})
    _id = ObjectId(user_document["_id"])
    print(_id)
    print(data)

    ak_count, m4_count, awp_count, mp5_count, med_kit_count, bandage_count, sp_count, lp_count = data.split('&')
    print(int(ak_count))
    updates = {
        "$inc": {"ak-47": int(ak_count),
                 "m4": int(m4_count),
                 "awp": int(awp_count),
                 "mp5": int(mp5_count),
                 "medkit": int(med_kit_count),
                 "bandage": int(bandage_count),
                 "speed_potion": int(sp_count),
                 "leaping_potion": int(lp_count),
                 "money": -1 * buy_sum}
    }
    print("bulbul")

    users_collection.update_one({"_id": _id}, updates)
    print("bulbulon")


def buy_shit(data, client_socket, client_address):
    print("buy shit")
    client_ip, client_port = client_address
    user_document = users_collection.find_one({"ip": client_ip, "port": client_port})
    ak_count, m4_count, awp_count, mp5_count, med_kit_count, bandage_count, sp_count, lp_count = data.split('&')

    buy_sum = (int(ak_count) * 2700 + int(m4_count) * 3100 + int(awp_count) * 4750 + int(mp5_count) * 1500 +
               int(med_kit_count) * 1000 + int(bandage_count) * 650 + int(sp_count) * 1800 + int(lp_count) * 1200)

    if buy_sum < user_document["money"]:
        update_user(data, client_address, buy_sum)
        print("Successful buy")
        client_socket.send("successful buy".encode())

    else:
        print("Unsuccessful buy - not enough money in user's account")
        client_socket.send("CHEATER".encode())


def join_game(data, client_socket, client_address):
    print("Inside join_game")
    client_ip, client_port = client_address
    user_document = users_collection.find_one({"ip": client_ip, "port": client_port})
    _id = ObjectId(user_document["_id"])
    ak_count, m4_count, awp_count, mp5_count, med_kit_count, bandage_count, sp_count, lp_count = data.split('&')

        # if ak_count <= 16 and ak_count <= user_document["ak-47"] and m4_count <= 16 and m4_count <= user_document["m4"] and awp_count <= 16 and awp_count <= user_document["awp"] and mp5_count <= 16 and mp5_count <= user_document["mp5"] and med_kit_count <= 16 and med_kit_count <= user_document["medkit"] and bandage_count <= 16 and bandage_count <= user_document["bandage"] and sp_count <= 16 and sp_count <= user_document["speed_potion"] and lp_count <= 16 and lp_count <= user_document["leaping_potion"]:

    items = {
        "ak-47": int(ak_count),
        "m4": int(m4_count),
        "awp": int(awp_count),
        "mp5": int(mp5_count),
        "medkit": int(med_kit_count),
        "bandage": int(bandage_count),
        "speed_potion": int(sp_count),
        "leaping_potion": int(lp_count)
    }
    print(2)

    for item, count in items.items():
        if count > 16 or count > user_document.get(item, 0):
            print("Cheater")
            client_socket.send("CHEATER".encode())
            return
        else:
            update = {"$inc": {item: -1 * count}}
            users_collection.update_one({"_id": _id}, update)
    client_socket.send("Joining_game".encode())

    #money = user_document["money"]
    money = 1000
    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.bind(("127.0.0.1",6969))
    lb_socket.send(f"JOIN&{client_port}&{money}&{int(ak_count)}&{int(m4_count)}&{int(awp_count)}&{int(mp5_count)}&{int(med_kit_count)}&{int(bandage_count)}&{int(sp_count)}&{int(lp_count)}".encode())
    print(f"Sending: JOIN&{client_port}&{money}&{int(ak_count)}&{int(m4_count)}&{int(awp_count)}&{int(mp5_count)}&{int(med_kit_count)}&{int(bandage_count)}&{int(sp_count)}&{int(lp_count)}")
    print("Successfully joined the game")

def handle_client(client_socket, client_address):
    """
    Handle a client request by parsing the request, determining the appropriate action, and responding accordingly.
    """

    while True:
        try:
            data = client_socket.recv(9192).decode()
            print("Received: ", data)
            # Parse the request data
            if data:
                method, data = data.split("%")
                if method == "Login":
                    print("Received login request")
                    login(client_socket, client_address, data)
                if method == "Sign_in":
                    print("Received sign in request")
                    sign_in(client_socket, client_address, data)
                if method == "Buy":
                    print("Received buy request")
                    buy_shit(data, client_socket, client_address)
                if method == "Play":
                    print("Received play request")
                    join_game(data, client_socket, client_address)
                    client_socket.close()
                    return
                if method == "Disconnect":
                    print("Received disconnect request")
                    change_connection_status(client_address, False)
                    print(f"{client_address} disconnected")
        except:
            pass

        """match method:
            case "Login":
                login(client_socket, client_address, data)

            case "Sign_in":
                sign_in(client_socket, client_address, data)

            case "Buy":
                print("buy")
                buy_shit(data, client_socket, client_address)

            case "Play":
                join_game(data, client_socket, client_address)
                client_socket.close()
                return

            case "Disconnect":
                change_connection_status(client_address, False)
                print(f"{client_address} disconnected")"""


def client_handler(client_socket, client_address):
    """
    Thread function to handle each client connection independently.
    """
    try:
        print("Trying to handle client: ", client_address)
        handle_client(client_socket, client_address)
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        change_connection_status(client_address, False)
        print(f"{client_address} disconnected because of the error")
    finally:
        client_socket.close()


def main():
    """
    Main function to initialize and run the server.
    """
    server_socket = socket.socket()
    server_socket.bind(("127.0.0.1", 6969))
    server_socket.listen()
    print("server up and running, listening at: 127.0.0.1, 6969")

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received from: ', client_address)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    main()
