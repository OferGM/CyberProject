import random
import socket
import threading
import time

connected = 1
SEARCH_CLOSEST_PLAYER_RATE = 0.1
LOAD_BALANCER_UDP_ADDR = ('127.0.0.1', 9999)

class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = []
        self.coordinates = {}
        self.disconnected = []
        self.mobs = {}
        self.playerChase = {}
        self.items = {}

    def GenerateMobs(self):
        if len(self.mobs) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = [
            random.randint(1, 50), 1, random.randint(1, 50), random.randint(0, 360)]
            self.mobs[id] = random_coordinates
            self.playerChase[id] = 0

    def GenerateItem(self,x,z):
        id = random.randint(10000000, 99999999)
        random_coordinates = [x, 1, z, random.randint(0, 360)]
        self.items[id] = random_coordinates

    def CreateMobString(self):
        mob_strings = ["aM&"]
        for id, coords in self.mobs.items():
            # Format each mob's data into "id&x&y&z"
            mob_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&{coords[3]}"
            mob_strings.append(mob_str)
        # Join all mob strings into one single string, separated by semicolons
        all_mobs_string = ";".join(mob_strings)
        return all_mobs_string

    def CreateItemString(self):
        item_strings = ["aI&"]
        items = ["potion of swiftness", "potion of leaping", "medkit", "bandage"]
        for id, coords in self.items.items():
            # Format each mob's data into "id&x&y&z"
            type = random.choice(items)
            item_str = f"{id}&{type}&{coords[0]}&{coords[1]}&{coords[2]}&"
            item_strings.append(item_str)
        # Join all mob strings into one single string, separated by semicolons
        all_items_string = ";".join(item_strings)
        return all_items_string

    def SendPositions(self, addr):
        data = self.CreateMobString()
        self.socket.sendto(data.encode(), addr)
        data = self.CreateItemString()
        print("sending: ", data)
        self.socket.sendto(data.encode(), addr)

    def start_server(self):
        try:
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()

            self.socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")
            threading.Thread(target=self.update_zombies).start()
            threading.Thread(target=self.handle_client).start()
        except Exception as e:
            print(f"Error starting server: {e}")

    def find_closest_player(self, zombieID):
        min_dist = 1000
        for clientID in self.coordinates.keys():
            total_dist = (float(self.coordinates[clientID][0]) - self.mobs[zombieID][0]) + \
                         (float(self.coordinates[clientID][1]) - self.mobs[zombieID][1])
            if total_dist <= min_dist:
                min_dist = total_dist
                self.playerChase[zombieID] = clientID

    def rotate_enemy(self, player_posit, enemy_posit):
        # Calculate vector from enemy to player
        dx = float(player_posit[0]) - float(enemy_posit[0])
        dy = float(player_posit[1]) - float(enemy_posit[1])
        dz = float(player_posit[2]) - float(enemy_posit[2])

        return 90

    def update_positions(self):
        for zombie_id in self.playerChase.keys():
            if connected == 1:
                zombie_x = float(self.mobs[zombie_id][0])
                zombie_y = float(self.mobs[zombie_id][1])
                zombie_z = float(self.mobs[zombie_id][2])
                playerID = int(self.playerChase[zombie_id])
                if playerID != 0:
                    player_coords = self.coordinates[str(playerID)]
                    player_x = float(player_coords[0])
                    player_y = float(player_coords[1])
                    player_z = float(player_coords[2])
                    self.mobs[zombie_id] = (1, 1, 1, 1)
                    self.mobs[zombie_id] = (
                    zombie_x + (player_x - zombie_x) * 0.01, zombie_y, zombie_z + (player_z - zombie_z) * 0.01,
                    self.rotate_enemy(player_coords, self.mobs[zombie_id]))

    def update_zombies(self):
        while (True):
            for zombieID in self.mobs.keys():
                self.find_closest_player(zombieID)
            self.update_positions()
            self.SendPositions(addr=LOAD_BALANCER_UDP_ADDR)
            time.sleep(SEARCH_CLOSEST_PLAYER_RATE)

    def handle_client(self):
        while(True):
            try:
                data, addr = self.socket.recvfrom(4096)
                data = data.decode()
                print("received: ", data)
                dataArr = data.split('&')
                if dataArr[0] == 'gSTATE':
                    msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}&{dataArr[6]}'
                    self.socket.sendto(msg.encode(), addr)
                    self.coordinates[dataArr[1]] = (dataArr[2], dataArr[3], dataArr[4], dataArr[5], dataArr[6])
                if dataArr[0] == 'gDEAD':
                    self.GenerateItem(self.mobs[int(dataArr[2])][0],self.mobs[int(dataArr[2])][2])
                    self.mobs.pop(int(dataArr[2]))
                    self.playerChase.pop(int(dataArr[2]))
                if dataArr[0] == 'gPICKED':
                    self.items.pop(int(dataArr[2]))

            except Exception as e:
                print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()