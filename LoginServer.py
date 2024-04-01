from dotenv import load_dotenv, find_dotenv
import os
import pprint
from pymongo import MongoClient
import PlayerInventory
import socket

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"

db_client = MongoClient(connection_string)

login_serverDB = db_client.login_server
collections = login_serverDB.list_collection_names()

print(collections)


def insert_new_user(username, user_password, client_address, client_port):
    collection = login_serverDB.users
    user_document = {
        "name": username,
        "password": user_password,
        "ip": client_address,
        "port": str(client_port),
        "inventory": {
            "weapons": {
                "ak-47": 0,
                "m4": 0,
                "awp": 0,
                "mp5": 0
            },
            "items": {
                "bandage": 0,
                "medkit": 0,
                "speed_potion": 0,
                "leaping_potion": 0
            }
        }
    }
    user_id = collection.insert_one(user_document).inserted_id


def login(client_socket, data):
    username, passwrd = data.split("&")
    collection = login_serverDB.users
    user_document = collection.find_one({"name": username, "password": passwrd})
    if user_document:
        client_socket.send(f"Login_successful&{user_document['_id']}".encode())
    else:
        client_socket.send("Login_failed".encode())


def sign_in(client_socket, client_address, data):
    username, passwrd = data.split("&")
    collection = login_serverDB.users
    user_document = collection.find_one({"name": username, "password": passwrd})
    if user_document:
        client_socket.send(f"Taken".encode())
    else:
        ip, port = client_address.split(",")
        insert_new_user(username, passwrd, ip, port)


def handle_client(client_socket, client_address):
    """
    Handle a client request by parsing the request, determining the appropriate action, and responding accordingly.
    """
    data = client_socket.recv(1024).decode()

    # Parse the request data
    method, data = data.split("%")

    match method:
        case "Login":
            login(client_socket, data)
        case "Sign in":
            sign_in(client_socket, client_address, data)


def main():
    """
    Main function to initialize and run the server.
    """
    server_socket = socket.socket()
    server_socket.bind(("0.0.0.0", 6969))
    server_socket.listen()

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        handle_client(client_socket, client_address)


if __name__ == "__main__":
    main()
