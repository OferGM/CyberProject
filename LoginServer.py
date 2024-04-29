from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
import socket
from bson.objectid import ObjectId
import threading

# Initialize socket connection to load balancer
lb_socket = socket.socket()
lb_socket.connect(("127.0.0.1", 8888))

# Load environment variables
load_dotenv(find_dotenv())

# MongoDB connection setup
password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"
db_client = MongoClient(connection_string)
login_serverDB = db_client.login_server
users_collection = login_serverDB.users


def change_connection_status(client_address, connected):
    """
    Update the connection status of a user in the database.

    Args:
        client_address (tuple): IP address and port of the client.
        connected (bool): New connection status.

    """
    ip, port = client_address
    user_document = users_collection.find_one({"ip": ip, "port": port})
    _id = ObjectId(user_document["_id"])
    update = {"$set": {"connected": connected}}
    users_collection.update_one({"_id": _id}, update)


def update_user_address(client_ip, client_port, user_id):
    """
    Update the IP address and port of a user in the database.

    Args:
        client_ip (str): IP address of the client.
        client_port (int): Port number of the client.
        user_id (str): User ID.

    """
    _id = ObjectId(user_id)
    updates = {"$set": {"ip": client_ip, "port": client_port}}
    users_collection.update_one({"_id": _id}, updates)


def insert_new_user(username, user_password, client_ip, client_port):
    """
    Insert a new user into the database.

    Args:
        username (str): Username of the new user.
        user_password (str): Password of the new user.
        client_ip (str): IP address of the client.
        client_port (int): Port number of the client.

    """
    user_document = {
        "name": username,
        "password": user_password,
        "ip": client_ip,
        "port": client_port,
        "money": 99999,
        "ak-47": 0,
        "m4": 0,
        "awp": 0,
        "mp5": 0,
        "medkit": 0,
        "bandage": 0,
        "speed_potion": 0,
        "leaping_potion": 0,
        "connected": True,
    }
    users_collection.insert_one(user_document)


def init_lobby(client_socket, user_document):
    """
    Initialize lobby for a user.

    Args:
        client_socket (socket): Client socket object.
        user_document (dict): User document from the database.

    """
    # Extract user inventory and money
    inventory = [user_document[item] for item in
                 ["ak-47", "m4", "awp", "mp5", "medkit", "bandage", "speed_potion", "leaping_potion"]]
    money = user_document["money"]
    response = "&".join(map(str, inventory)) + f"&{money}"
    print("Current state: ", response)
    client_socket.send(response.encode())


def login(client_socket, client_address, data):
    """
    Login a user.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing username and password separated by '&'.

    """
    username, password = data.split("&")
    user_document = users_collection.find_one({"name": username, "password": password})
    if user_document:
        if not user_document["connected"]:
            ip, port = client_address
            update_user_address(ip, port, user_document["_id"])
            client_socket.send("Login_successful".encode())
            change_connection_status(client_address, True)
            print(f"{client_address} is now logged in")
            init_lobby(client_socket, user_document)
        else:
            client_socket.send("User_already_connected".encode())
    else:
        client_socket.send("Login_failed".encode())


def sign_in(client_socket, client_address, data):
    """
    Sign up a new user.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing username and password separated by '&'.

    """
    username, password = data.split("&")
    user_document = users_collection.find_one({"name": username})
    if user_document:
        client_socket.send("Taken".encode())
    else:
        ip, port = client_address
        insert_new_user(username, password, ip, port)
        client_socket.send("Sign_in_successful".encode())
        user_document = users_collection.find_one({"name": username})
        change_connection_status(client_address, True)
        print(f"{client_address} is now logged into the game")
        init_lobby(client_socket, user_document)


def update_user(data, client_address, shmoney):
    """
    Update user data in the database.

    Args:
        data (list[str]): Data containing inventory counts.
        client_address (tuple): IP address and port of the client.
        shmoney (int): Amount of money to be updated.

    """
    ip, port = client_address
    user_document = users_collection.find_one({"ip": ip, "port": port})
    _id = ObjectId(user_document["_id"])
    ak_count = data[0]
    m4_count = data[1]
    awp_count = data[2]
    mp5_count = data[3]
    med_kit_count = data[4]
    bandage_count = data[5]
    sp_count = data[6]
    lp_count = data[7]
    updates = {
        "$inc": {"ak-47": int(ak_count),
                 "m4": int(m4_count),
                 "awp": int(awp_count),
                 "mp5": int(mp5_count),
                 "medkit": int(med_kit_count),
                 "bandage": int(bandage_count),
                 "speed_potion": int(sp_count),
                 "leaping_potion": int(lp_count),
                 "money": shmoney}
    }

    users_collection.update_one({"_id": _id}, updates)


def buy_shit(data, client_socket, client_address):
    """
    Handle buying items by a user.

    Args:
        data (str): Data containing inventory counts separated by '&'.
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.

    """

    client_ip, client_port = client_address
    user_document = users_collection.find_one({"ip": client_ip, "port": client_port})
    inventory_counts = map(int, data.split('&'))
    buy_sum = sum(
        count * price for count, price in zip(inventory_counts, [2700, 3100, 4750, 1500, 1000, 650, 1800, 1200]))
    if buy_sum < user_document["money"]:
        update_user(data.split("&"), client_address, -1 * buy_sum)
        client_socket.send("successful buy".encode())
    else:
        client_socket.send("CHEATER".encode())


def join_game(data, client_socket, client_address):
    """
    Handle user joining a game.

    Args:
        data (str): Data containing inventory counts separated by '&'.
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.

    """
    client_ip, client_port = client_address
    user_document = users_collection.find_one({"ip": client_ip, "port": client_port})
    inventory_counts = map(int, data.split('&'))
    for item, count in zip(["ak-47", "m4", "awp", "mp5", "medkit", "bandage", "speed_potion", "leaping_potion"],
                           inventory_counts):
        if count > 16 or count > user_document.get(item, 0):
            client_socket.send("CHEATER".encode())
            return
        else:
            update = {"$inc": {item: -1 * count}}
            users_collection.update_one({"_id": ObjectId(user_document["_id"])}, update)
    client_socket.send("Joining_game".encode())
    money = user_document["money"]
    lb_socket.send(f"JOIN&{client_port}&{money}&{data}".encode())


def disconnect_from_game(client_socket, client_address, data):
    """
    Handle user disconnecting from a game.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing updated money amount.

    """
    print("disconnect")
    port, shmoney = int(data.split("&")[0]), int(data.split("&")[1])
    client_address = ("127.0.0.1", port)
    update_user(data.split("&")[2:], client_address, shmoney)
    print("sending disconnect")
    client_socket.send("successfully_disconnected".encode())


def handle_client(client_socket, client_address):
    """
    Handle a client request.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.

    """
    while True:
        try:
            data = client_socket.recv(9192).decode()
            if data:
                method, data = data.split("%")
                print(method)
                if method == "Login":
                    login(client_socket, client_address, data)
                if method == "Sign_in":
                    sign_in(client_socket, client_address, data)
                if method == "Buy":
                    buy_shit(data, client_socket, client_address)
                if method == "Play":
                    join_game(data, client_socket, client_address)
                if method == "Disconnect":
                    disconnect_from_game(client_socket, client_address, data)
                if method == "Rape_Disconnect":
                    print(data)
                    client_address1 = ("127.0.0.1", int(data))
                    change_connection_status(client_address1, False)
                if method == "GIMME":
                    print("gimme")
                    ip, port = client_address
                    user_document = users_collection.find_one({"ip": ip, "port": port})
                    init_lobby(client_socket, user_document)
        except:
            pass


def client_handler(client_socket, client_address):
    """
    Handle each client connection in a separate thread.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.

    """
    try:
        handle_client(client_socket, client_address)
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        change_connection_status(client_address, False)
    finally:
        client_socket.close()


def main():
    """
    Initialize and run the server.

    """
    server_socket = socket.socket()
    server_socket.bind(("127.0.0.1", 6969))
    server_socket.listen()
    print("Server up and running, listening at: 127.0.0.1, 6969")

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received from: ', client_address)
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    main()
