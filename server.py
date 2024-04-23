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
        self.all_players = {}
        self.coordinates = {}
        self.mobs = {}
        self.playerChase = {}
        self.items = {}
        self.chat_messages = []

    def GenerateMobs(self):
        if len(self.mobs) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = [
            random.randint(1, 50), 1.5, random.randint(1, 50), random.randint(0, 360) ,100]
            self.mobs[id] = random_coordinates
            self.playerChase[id] = 0

    def GenerateItem(self,x,z):
        id = random.randint(10000000, 99999999)
        random_coordinates = [x, 1, z, random.randint(0, 360)]
        self.items[id] = random_coordinates

    def CreateMobString(self):
        mob_strings = ["aM&"]
        for id, coords in self.mobs.items():
            # Format each mob's data into "id&x&y&z&health"
            mob_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&{coords[3]}&{coords[4]}"
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
        # print("sending: ", data)
        self.socket.sendto(data.encode(), addr)

    def start_server(self):
        try:
            for i in range(10):
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
            total_dist = abs((abs(float(self.coordinates[clientID][0])) - abs(self.mobs[zombieID][0]))) + \
                         abs((abs(float(self.coordinates[clientID][1])) - abs(self.mobs[zombieID][1])))
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
                current_zombie_data = self.mobs[zombie_id]
                playerID = int(self.playerChase[zombie_id])
                if playerID != 0 and str(playerID) in self.coordinates:
                    player_coords = self.coordinates[str(playerID)]
                    player_x = float(player_coords[0])
                    player_z = float(player_coords[2])
                    # Only update position, keep other data like health unchanged.
                    self.mobs[zombie_id] = (
                        current_zombie_data[0] + (player_x - current_zombie_data[0]) * 0.01,
                        current_zombie_data[1],
                        current_zombie_data[2] + (player_z - current_zombie_data[2]) * 0.01,
                        current_zombie_data[3],
                        current_zombie_data[4]  # Preserve existing health
                    )
    def update_zombies(self):
        while (True):
            if len(self.mobs) < 30:
                self.GenerateMobs()
            for zombieID in self.mobs.keys():
                self.find_closest_player(zombieID)
            self.update_positions()
            self.SendPositions(addr=LOAD_BALANCER_UDP_ADDR)
            time.sleep(SEARCH_CLOSEST_PLAYER_RATE)

    def handle_client(self):
        while(True):
            try:
                data, addr = self.socket.recvfrom(9192)
                data = data.decode()
                # print("received: ", data)
                dataArr = data.split('&')
                if dataArr[0] == 'JOIN':
                    playerID = dataArr[1]
                    print("new player joined: ", playerID)
                    self.all_players[playerID] = dataArr[2:]
                if dataArr[0] == 'gSTATE':
                    msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}&{dataArr[6]}'
                    self.socket.sendto(msg.encode(), addr)
                    self.coordinates[dataArr[1]] = (dataArr[2], dataArr[3], dataArr[4], dataArr[5], dataArr[6])
                if dataArr[0] == 'gDEAD':
                    self.GenerateItem(self.mobs[int(dataArr[2])][0],self.mobs[int(dataArr[2])][2])
                    self.mobs.pop(int(dataArr[2]))
                    self.playerChase.pop(int(dataArr[2]))
                    self.socket.sendto(f"aR&{int(dataArr[2])}".encode(), addr)
                if dataArr[0] == 'gPICKED':
                    self.items.pop(int(dataArr[2]))
                    self.socket.sendto(f"aPICKED&{dataArr[2]}".encode(), addr)
                if dataArr[0] == 'gDAMAGE':
                    self.coordinates[dataArr[1]] = (self.coordinates[dataArr[1]][0], self.coordinates[dataArr[1]][1], self.coordinates[dataArr[1]][2], self.coordinates[dataArr[1]][3], dataArr[2])
                    print(f"Player {int(dataArr[1])} hurt and his health is {dataArr[2]}")
                    self.socket.sendto(f"aH&{int(dataArr[1])}&{dataArr[2]}".encode(), addr)
                if dataArr[0] == 'gDAMAGEMOB':
                    print("DAMAGED MOB")
                    mob_id = int(dataArr[2])  # Ensuring that the mob ID is an integer
                    damage = int(dataArr[3])  # Ensuring that the damage is an integer
                    print("damage:",damage)
                    print(self.mobs[mob_id][4])

                    if mob_id in self.mobs:
                        current_health = self.mobs[mob_id][4]
                        print(f"Before damage: Zombie {mob_id} health is {current_health}")
                        new_health = current_health - damage
                        self.mobs[mob_id] = (
                        self.mobs[mob_id][0], self.mobs[mob_id][1], self.mobs[mob_id][2], self.mobs[mob_id][3],
                        new_health)
                        print(f"After damage: Zombie {mob_id} health is {self.mobs[mob_id][4]}")

                        if new_health <= 0:
                            print("DEAD")
                            self.GenerateItem(self.mobs[mob_id][0], self.mobs[mob_id][2])
                            self.mobs.pop(mob_id)
                            self.playerChase.pop(mob_id)
                            self.socket.sendto(f"aR&{mob_id}".encode(), addr)
                if dataArr[0] == 'gDisconnect':
                    self.all_players.pop(dataArr[1], None)
                    self.coordinates.pop(dataArr[1], None)
                    self.playerChase.pop(dataArr[1], None)


            except Exception as e:
                print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()