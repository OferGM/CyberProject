import time

from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
import socket
from bson.objectid import ObjectId
import threading
import random
from sympy import randprime


def get_private_ip():
    # Create a socket connection to a remote server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This IP and port are arbitrary and don't need to be reachable
        # We just need to open a socket and get the local address used
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
    except Exception as e:
        private_ip = "Unable to determine IP address: " + str(e)
    finally:
        s.close()
    return private_ip


private_ip = get_private_ip()
print(private_ip)

lb_ip = input("Fill the ip of the load-balancer")

# Initialize socket connection to load balancer
lb_socket = socket.socket()
lb_socket.connect((lb_ip, 8888))

# Receive prime and base from the server
prime = int(lb_socket.recv(1024).decode())
base = int(lb_socket.recv(1024).decode())

# Generate client's private key
private_key_client = random.randint(1, prime - 1)  # Assume this is generated securely

# Calculate public key to send to the server
public_key_client = pow(base, private_key_client, prime)
lb_socket.send(f"{public_key_client}".encode())

# Receive server's public key
public_key_server = int(lb_socket.recv(1024).decode())

# Calculate shared secret
shared_secret_lb = pow(public_key_server, private_key_client, prime)

# Load environment variables
load_dotenv(find_dotenv())

# MongoDB connection setup
password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"
db_client = MongoClient(connection_string)
login_serverDB = db_client.login_server
users_collection = login_serverDB.users
shared_secrets = {}
public_keys = {}


def change_connection_status(client_address, connected):
    """
    Update the connection status of a user in the database.

    Args:
        client_address (tuple): IP address and port of the client.
        connected (bool): New connection status.

    """
    ip, port = client_address
    print("client address is: ", client_address)
    user_document = users_collection.find_one({"ip": ip, "port": port})
    print("found!")
    _id = ObjectId(user_document["_id"])
    update = {"$set": {"connected": connected}}
    users_collection.update_one({"_id": _id}, update)

def change_connection_status_id(clientID, connected):
    """
    Update the connection status of a user in the database.

    Args:
        client_address (tuple): IP address and port of the client.
        connected (bool): New connection status.

    """
    user_document = users_collection.find_one({"_id": clientID})
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


def init_lobby(client_socket, user_document, clientID):
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
    client_socket.send(encrypt(response, clientID))


def login(client_socket, client_address, data, clientID):
    """
    Login a user.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing username and password separated by '&'.
        clientID
    """
    username, password = data.split("&")
    user_document = users_collection.find_one({"name": username, "password": password})
    if user_document:
        if not user_document["connected"]:
            ip, port = client_address
            update_user_address(ip, port, user_document["_id"])
            client_socket.send(encrypt("Login_successful", clientID))
            change_connection_status(client_address, True)
            print(f"{client_address} is now logged in")
            init_lobby(client_socket, user_document, clientID)
        else:
            client_socket.send(encrypt("User_already_connected", clientID))
    else:
        client_socket.send(encrypt("Login_failed", clientID))


def sign_in(client_socket, client_address, data, clientID):
    """
    Sign up a new user.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing username and password separated by '&'.

    """
    print("poopyu")
    username, password = data.split("&")
    user_document = users_collection.find_one({"name": username})
    print("kak")
    if user_document:
        print("kaki")
        client_socket.send(encrypt("Taken", clientID))
    else:
        print("kaka")
        ip, port = client_address
        insert_new_user(username, password, ip, port)
        client_socket.send(encrypt("Sign_in_successful", clientID))
        user_document = users_collection.find_one({"name": username})
        change_connection_status(client_address, True)
        print(f"{client_address} is now logged into the game")
        init_lobby(client_socket, user_document, clientID)


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

def update_user_by_id(inventory_data, clientID, shmoney):
    """
    Update user data in the database.

    Args:
        data (list[str]): Data containing inventory counts.
        client_address (tuple): IP address and port of the client.
        shmoney (int): Amount of money to be updated.

    """
    user_document = users_collection.find_one({"_id": ObjectId(clientID)})
    if user_document:
        updates = {
            "$set": {
                "money": shmoney,
                "ak-47": int(inventory_data[0]),
                "m4": int(inventory_data[1]),
                "awp": int(inventory_data[2]),
                "mp5": int(inventory_data[3]),
                "medkit": int(inventory_data[4]),
                "bandage": int(inventory_data[5]),
                "speed_potion": int(inventory_data[6]),
                "leaping_potion": int(inventory_data[7])
            }
        }
        users_collection.update_one({"_id": ObjectId(clientID)}, updates)

def buy_shit(data, client_socket, client_address, clientID):
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
        client_socket.send(encrypt("successful buy", clientID))
    else:
        client_socket.send(encrypt("CHEATER", clientID))


def join_game(data, client_socket, client_address, clientID):
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
            client_socket.send(encrypt("CHEATER", clientID))
            return
        else:
            update = {"$inc": {item: -1 * count}}
            users_collection.update_one({"_id": ObjectId(user_document["_id"])}, update)
    client_socket.send(encrypt("Joining_game", clientID))
    money = user_document["money"]
    lb_socket.send(encrypt_login(f"JOIN&{client_port}&{money}&{data}"))


def disconnect_from_game(client_socket, client_address, data, clientID):
    """
    Handle user disconnecting from a game.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.
        data (str): Data containing updated money amount and inventory items.
        clientID (int): Client's unique identifier.

    """
    print("disconnect")
    data_parts = data.split("&")
    ip = int(data_parts[0])
    port = int(data_parts[1])
    shmoney = int(data_parts[2])
    inventory_data = data_parts[3:]  # This assumes the inventory data starts from the third element

    # Update the user's money and inventory in the database
    update_user_by_id(inventory_data, clientID, shmoney)
    print("sending disconnect")
    change_connection_status((ip, port), False)
    client_socket.send(encrypt("successfully_disconnected", clientID))


def handle_client(client_socket, client_address):
    """
    Handle a client request.

    Args:
        client_socket (socket): Client socket object.
        client_address (tuple): IP address and port of the client.

    """
    while True:
        try:
            data = client_socket.recv(9192)
            if data:
                indi = data.split(b'&')
                clientID = int(indi[0].decode('ascii', 'ignore'))
                print("id: ", clientID)
                data = decrypt(data)
                print(data)
                method, data = data.split("%")
                print(method)
                if method == "Login":
                    login(client_socket, client_address, data, clientID)
                if method == "Sign_in":
                    sign_in(client_socket, client_address, data, clientID)
                if method == "Buy":
                    buy_shit(data, client_socket, client_address, clientID)
                if method == "Play":
                    join_game(data, client_socket, client_address, clientID)
                if method == "Disconnect":
                    disconnect_from_game(client_socket, client_address, data, clientID)
                if method == "Rape_Disconnect":
                    print(data)
                    print ("rape disconnect")
                    data = data.split("&")
                    client_address1 = (int(data[0], clientID))
                    change_connection_status(client_address1, False)
                if method == "GIMME":
                    print("gimme")
                    ip, port = client_address
                    user_document = users_collection.find_one({"ip": ip, "port": port})
                    init_lobby(client_socket, user_document, clientID)
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


def gen_prime():
    # Function to generate a large prime number
    return randprime(2 ** 1023, 2 ** 1024 - 1)


def gen_primitive_root(p):
    while True:
        g = random.randint(2, p - 1)
        if pow(g, (p - 1) // 2, p) != 1 and pow(g, 2, p) != 1:
            return g


def diffie_program():
    host = '0.0.0.0'
    port = 7878

    prime = gen_prime()
    base = gen_primitive_root(prime)  # You can choose any suitable base, typically a primitive root modulo prime

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)
    while (True):
        connection, address = server_socket.accept()

        # Send prime and base to the client
        connection.send(str(prime).encode())
        connection.send(str(base).encode())

        # Generate server's private key
        private_key_server = random.randint(1, prime - 1)

        # Calculate public key to send to the client
        public_key_server = pow(base, private_key_server, prime)
        time.sleep(1)
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
        shared_secrets[public_key_client] = shared_secret
        public_keys[client_id] = public_key_client


def decrypt(data):
    # Convert key to bytes (using 4 bytes and little endian byteorder)
    indi = data.split(b'&', 1)
    print('rar')
    clientID = int(indi[0].decode('ascii', 'ignore'))
    print("id: ", clientID)
    shared_key = shared_secrets[public_keys[clientID]]
    data = indi[1]
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the encrypted message and the key
    decrypted_bytes = bytes([encrypted_byte ^ key_byte for encrypted_byte, key_byte in zip(data, key_bytes)])
    # Convert the decrypted bytes back to a string
    decrypted_message = decrypted_bytes.decode('ascii', 'ignore')
    print("i love little kids: ", decrypted_message)
    return decrypted_message


def encrypt(data, clientID):
    # Convert message and key to byte arrays
    shared_key = shared_secrets[public_keys[clientID]]
    message_bytes = data.encode('ascii', 'ignore')
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the message and the key
    encrypted_bytes = bytes([message_byte ^ key_byte for message_byte, key_byte in zip(message_bytes, key_bytes)])
    print(encrypted_bytes)
    return encrypted_bytes


def encrypt_login(data):
    # Convert message and key to byte arrays
    message_bytes = data.encode('ascii', 'ignore')
    key_bytes = shared_secret_lb.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the message and the key
    encrypted_bytes = bytes([message_byte ^ key_byte for message_byte, key_byte in zip(message_bytes, key_bytes)])
    print(encrypted_bytes)
    return encrypted_bytes


def main():
    """
    Initialize and run the server.

    """
    diffie = threading.Thread(target=diffie_program, args=())
    diffie.start()
    server_socket = socket.socket()
    server_socket.bind(("0.0.0.0", 6969))
    server_socket.listen()
    print("Server up and running, listening at: 0.0.0.0, 6969")

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received from: ', client_address)
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    main()
