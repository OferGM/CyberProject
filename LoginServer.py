from dotenv import load_dotenv, find_dotenv
import os
import pprint
from pymongo import MongoClient

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb+srv://ofergmizrahi:{password}@logininfo.vytelui.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

login_serverDB = client.login_server
game_serverDB = client.game_server
collections = login_serverDB.list_collection_names()
print(collections)


def insert_new_user(username, user_password, client_address, client_port):
    collection = login_serverDB.users
    user_document = {
        "name": username,
        "password": user_password,
        "ip": client_address,
        "port": client_port,
        "inventory": {
            "weapons": {
                "ak-47": {
                    "quantity": 0,
                    "7.62x39mm": 0
                },
                "m4": {
                    "quantity": 0,
                    "5.56x45mm": 0
                },
                "awp": {
                    "quantity": 0,
                    "7.62x51mm": 0
                },
                "mp5": {
                    "quantity": 0,
                    "9mm": 0
                }
            },
            "items": {
                "bandage": 0,
                "medkit": 0
            }
        }
    }
    user_id = collection.insert_one(user_document).inserted_id
    print(user_id)


def insert_starting_inventory(username, user_password, client_address, client_port, player_inventory):
    collection = login_serverDB.users
    weapons = player_inventory.get_weapons()
    user_document = {
        "name": username,
        "password": user_password,
        "ip": client_address,
        "port": client_port,
        "inventory": {
            "weapons": {
                "ak-47": {
                    "quantity": 0,
                    "7.62x39mm": 0
                },
                "m4": {
                    "quantity": 0,
                    "5.56x45mm": 0
                },
                "awp": {
                    "quantity": 0,
                    "7.62x51mm": 0
                },
                "mp5": {
                    "quantity": 0,
                    "9mm": 0
                }
            },
            "items": {
                "bandage": 0,
                "medkit": 0
            }
        }
    }
    user_id = collection.insert_one(user_document).inserted_id
    print(user_id)


insert_new_user("FatHalaf", "ILOVEFOOD")
