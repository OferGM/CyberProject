import random
import socket
import threading
import time
import queue
import ChatServer

connected = 1
SEARCH_CLOSEST_PLAYER_RATE = 0.1
LOAD_BALANCER_UDP_ADDR = ()
servers_dict = {1: (), 2: (), 3: (), 4: (),
                 'login': ()}


class Server:
    def __init__(self, addr):
        self.host = addr[0]
        self.port = addr[1]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.all_players = {}
        self.coordinates = {}
        self.mobs = {}
        self.playerChase = {}
        self.witches = {}
        self.playerChaseWitches = {}
        self.playerChaseOrbs = {}
        self.items = {}
        self.chat_messages = []
        self.orbs = {}
        self.heldItems = {}
        self.chests = {} # chests[id] = [x,y,z,item1,item2,...,item[n]]


    def GenerateChest(self,x,y,z,items):
        id = random.randint(10000000, 99999999)
        list = [x,y,z]
        for item in items:
            list.append(item)
        self.chests[id] = list
        print("hi")
        packet = self.CreateChestString()
        self.socket.sendto(packet.encode(), LOAD_BALANCER_UDP_ADDR)



    def GenerateMobs(self):
        if len(self.mobs) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = [
            random.randint(-200, 200), 1.5, random.randint(-200, 200), random.randint(0, 360) ,100]
            self.mobs[id] = random_coordinates
            self.playerChase[id] = 0

    def GenerateOrbs(self,x,y,z,playerToChase):
        id = random.randint(10000000, 99999999)
        random_coordinates = [x,y,z]
        self.orbs[id] = random_coordinates
        self.playerChaseOrbs[id] = playerToChase
    def GenerateWitches(self):
        if len(self.witches) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = [
                random.randint(-200, 200), 3, random.randint(-200, 200), random.randint(0, 360), 100, time.time()
                # Last orb shot time
            ]
            self.witches[id] = random_coordinates
            self.playerChaseWitches[id] = 0

    def GenerateItem(self,x,z):
        id = random.randint(10000000, 99999999)
        random_coordinates = [x, 1, z, random.randint(0, 360)]
        self.items[id] = random_coordinates

    def RemoveChest(self,clientID,id):
        self.chests.pop(int(id))
        self.socket.sendto(f"aREMOVECHEST&{clientID}&{id}".encode(), LOAD_BALANCER_UDP_ADDR)

    def CreateChestString(self):
        chest_strings = ["aC&"]
        for id, items in self.chests.items():
            chest_str = f"{id}&{'&'.join(map(str, items))}"  # Convert items to string to ensure no list is inside
            chest_strings.append(chest_str)
        all_chest_strings = ';'.join(chest_strings)
        return all_chest_strings

    def CreateMobString(self):
        mob_strings = ["aM&"]
        for id, coords in self.mobs.items():
            # Format each mob's data into "id&x&y&z&health"
            mob_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&{coords[3]}&{coords[4]}"
            mob_strings.append(mob_str)
        # Join all mob strings into one single string, separated by semicolons
        all_mobs_string = ";".join(mob_strings)
        return all_mobs_string

    def handle_damage_witch(self, witch_id, damage_amount):
        """Apply damage to a witch and handle witch death."""
        if witch_id in self.witches:
            current_health = self.witches[witch_id][4]
            new_health = current_health - damage_amount
            print(f"Witch {witch_id} damaged: {damage_amount} damage, {new_health} health remaining.")

            if new_health <= 0:
                print(f"Witch {witch_id} has died.")
                # Remove the witch from the dictionary
                witch = self.witches.pop(witch_id)
                self.playerChaseWitches.pop(witch_id)
                # Handle additional cleanup or game logic, like spawning items
                self.GenerateItem(witch[0], witch[2])
                # Notify clients
                self.socket.sendto(f"aWDEAD&{witch_id}".encode(), LOAD_BALANCER_UDP_ADDR)
            else:
                # Update witch's health in the dictionary
                self.witches[witch_id] = (
                    self.witches[witch_id][0],
                    self.witches[witch_id][1],
                    self.witches[witch_id][2],
                    self.witches[witch_id][3],
                    new_health,
                    self.witches[witch_id][5]  # Preserve last orb shot time
                )

    def witch_shoot_orb(self, witch_id, playerID):
        current_time = time.time()
        orb_cooldown = 20  # Cooldown in seconds, adjust as needed

        # Check if enough time has elapsed since the last orb was shot
        if current_time - self.witches[witch_id][5] > orb_cooldown:
            # Update the last orb shot time
            self.witches[witch_id] = (self.witches[witch_id][0],self.witches[witch_id][1],self.witches[witch_id][2],self.witches[witch_id][3],self.witches[witch_id][4],current_time)
            # Generate the orb
            self.GenerateOrbs(self.witches[witch_id][0], self.witches[witch_id][1], self.witches[witch_id][2], playerID)
        else:
            pass
        pass

    def CreateWitchString(self):
        witch_strings = ["aW&"]
        for id, coords in self.witches.items():
            # Format each mob's data into "id&x&y&z&health"
            witch_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&{coords[3]}&{coords[4]}"
            witch_strings.append(witch_str)
        # Join all mob strings into one single string, separated by semicolons
        all_mobs_string = ";".join(witch_strings)
        return all_mobs_string

    def update_witches(self):
        while True:
            for witch_id in list(self.witches.keys()):
                self.find_closest_player_for_witch(witch_id)
            for witch_id in list(self.witches.keys()):
                if connected == 1:
                    current_witch_data = self.witches[witch_id]
                    playerID = int(self.playerChaseWitches[witch_id])
                    if playerID != 0 and str(playerID) in self.coordinates:
                        player_coords = self.coordinates[str(playerID)]
                        player_x = float(player_coords[0])
                        player_z = float(player_coords[2])
                        distance = ((current_witch_data[0] - player_x) ** 2 + (
                                    current_witch_data[2] - player_z) ** 2) ** 0.5

                        if distance > 14:
                            # Update position towards the player
                            self.witches[witch_id] = (
                                current_witch_data[0] + (player_x - current_witch_data[0]) * 0.02,
                                current_witch_data[1],
                                current_witch_data[2] + (player_z - current_witch_data[2]) * 0.02,
                                current_witch_data[3],
                                current_witch_data[4],
                                current_witch_data[5]  # Maintain the last orb shot time
                            )
                        elif distance < 14:
                            self.witch_shoot_orb(witch_id, str(playerID))
            time.sleep(SEARCH_CLOSEST_PLAYER_RATE)

    def find_closest_player_for_witch(self, witchID):
        min_dist = 1000
        for clientID in self.coordinates.keys():
            total_dist = abs((abs(float(self.coordinates[clientID][0])) - abs(self.witches[witchID][0]))) + \
                         abs((abs(float(self.coordinates[clientID][2])) - abs(self.witches[witchID][2])))
            if total_dist <= min_dist:
                min_dist = total_dist
                self.playerChaseWitches[witchID] = clientID
        if min_dist > 70:
            self.playerChaseWitches[witchID] = 0

    def update_orbs(self):
        while True:
            # Go through all orbs in the dictionary
            for orb_id in list(self.orbs.keys()):
                if orb_id in self.orbs and orb_id in self.playerChaseOrbs:
                    target_player_id = self.playerChaseOrbs[orb_id]
                    if str(target_player_id) in self.coordinates:
                        orb_position = self.orbs[orb_id]
                        player_position = self.coordinates[str(target_player_id)]

                        # Calculate movement towards the player
                        dx = float(player_position[0]) - orb_position[0]
                        dz = float(player_position[2]) - orb_position[2]
                        distance = (dx ** 2 + dz ** 2) ** 0.5

                        # Define orb speed
                        orb_speed = 0.5  # Adjust speed as needed

                        # Update orb position
                        if distance > 15:
                            self.socket.sendto(f"aRemoveOrb&{orb_id}".encode(), LOAD_BALANCER_UDP_ADDR)
                            self.orbs.pop(orb_id, None)
                        if distance > 1.5:
                            normalized_dx = dx / distance
                            normalized_dz = dz / distance
                            new_x = orb_position[0] + normalized_dx * orb_speed
                            new_z = orb_position[2] + normalized_dz * orb_speed
                            self.orbs[orb_id] = [new_x, orb_position[1], new_z]
                        else:
                            # Handle collision with player
                            self.apply_orb_damage_to_player(target_player_id, orb_id)
                            continue
            time.sleep(SEARCH_CLOSEST_PLAYER_RATE)

    def apply_orb_damage_to_player(self, player_id, orb_id):
        damage = 20  # Define damage
        player_health = int(self.coordinates[player_id][4]) - damage
        self.coordinates[player_id] = (
            self.coordinates[player_id][0],
            self.coordinates[player_id][1],
            self.coordinates[player_id][2],
            self.coordinates[player_id][3],
            player_health
        )
        # Inform client about the new health
        self.socket.sendto(f"aH&{player_id}&{player_health}".encode(), LOAD_BALANCER_UDP_ADDR)
        # Remove the orb after it hits a player
        print("ORB EXPLODED")
        self.socket.sendto(f"aRemoveOrb&{orb_id}".encode(), LOAD_BALANCER_UDP_ADDR)
        self.orbs.pop(orb_id, None)
        pass

    def createOrbString(self):
        orb_strings = ["aO&"]  # Start with a unique identifier for orb updates, e.g., "aO&"
        for orb_id, coords in self.orbs.items():
            # Format each orb's data into "id&x&y&z"
            orb_str = f"{orb_id}&{coords[0]}&{coords[1]}&{coords[2]}"
            orb_strings.append(orb_str)
        # Join all orb strings into one single string, separated by semicolons
        all_orbs_string = ";".join(orb_strings)
        return all_orbs_string

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
        self.socket.sendto(data.encode(), addr)
        data = self.CreateWitchString()
        self.socket.sendto(data.encode(),addr)
        orb_data = self.createOrbString()
        if orb_data != 'a0&':
            self.socket.sendto(orb_data.encode(), addr)  # Send orb data to clients

    def start_server(self):
        if serverNum == 4:
            chatThread = threading.Thread(target=ChatServer.Chat)
            chatThread.start()
        try:
            for i in range(22):
                self.GenerateMobs()
            for i in range(3):
                pass#self.GenerateWitches()

            self.socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")
            threading.Thread(target=self.update_zombies).start()
            threading.Thread(target=self.update_witches).start()
            threading.Thread(target=self.handle_client).start()
            threading.Thread(target=self.update_orbs).start()
        except Exception as e:
            print(f"Error starting server: {e}")

    def find_closest_player(self, zombieID):
        min_dist = 1000
        for clientID in self.coordinates.keys():
            total_dist = abs((abs(float(self.coordinates[clientID][0])) - abs(self.mobs[zombieID][0]))) + \
                         abs((abs(float(self.coordinates[clientID][2])) - abs(self.mobs[zombieID][2])))
            if total_dist <= min_dist:
                min_dist = total_dist
                self.playerChase[zombieID] = clientID
        if min_dist > 45:
            self.playerChase[zombieID] = 0

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
            # if len(self.mobs) < 30:
            #     self.GenerateMobs()
            for zombieID in self.mobs.keys():
                self.find_closest_player(zombieID)
            self.update_positions()
            self.SendPositions(addr=LOAD_BALANCER_UDP_ADDR)
            time.sleep(SEARCH_CLOSEST_PLAYER_RATE)

    def handle_client(self):
        while(True):
            #try:
                data, addr = self.socket.recvfrom(9192)
                data = data.decode()
                print("Received: ", data)
                dataArr = data.split('&')
                if dataArr[0] == 'JOIN':
                    playerID = dataArr[1]
                    print("new player joined: ", playerID)
                    darr = data.split('&', 2)
                    data = darr[2]
                    self.all_players[playerID] = data
                    print("KAKIIIIIIIIIIIIIIIIIIIIIIIIIIII: ", data)
                    #self.coordinates[playerID] = 0
                if dataArr[0] == 'gSTATE':
                    playerID = dataArr[1]
                    if dataArr[1] in self.heldItems and playerID in self.all_players:
                        print("SENDING STATE!!!!!")
                        msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}&{dataArr[6]}&{self.heldItems[dataArr[1]]}'
                        self.socket.sendto(msg.encode(), addr)
                        self.coordinates[dataArr[1]] = (dataArr[2], dataArr[3], dataArr[4], dataArr[5], dataArr[6])
                    else:
                        if playerID in self.all_players:
                            print("SENDING STATE!!!!!")
                            msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}&{dataArr[6]}&NONE'
                            self.socket.sendto(msg.encode(), addr)
                            self.coordinates[dataArr[1]] = (dataArr[2], dataArr[3], dataArr[4], dataArr[5], dataArr[6])
                if dataArr[0] == 'STATE':
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
                if dataArr[0] == 'zDAMAGEMOB':
                    print("DAMAGED MOB")
                    mob_id = int(dataArr[2])  # Ensuring that the mob ID is an integer
                    damage = int(dataArr[3])  # Ensuring that the damage is an integer
                    print("damage:",damage)
                    #print(self.mobs[mob_id][4])

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
                    print(f"Disconnecting: ", dataArr[1])
                    self.all_players.pop(int(dataArr[1]), None)
                    self.coordinates.pop((dataArr[1]), None)
                    #self.playerChase.pop((dataArr[1]), None)
                    self.socket.sendto(f"DISCONNECT&{dataArr[1]}".encode(), addr)
                    login_socket = socket.socket()
                    login_socket.connect((servers_dict['login'][0], 6969))
                    login_socket.send(f"Rape_Disconnect%{dataArr[1]}".encode())
                    login_socket.close()
                if dataArr[0] == 'gSafeDisconnect':
                    self.all_players.pop(int(dataArr[1]), None)
                    self.coordinates.pop(int(dataArr[1]), None)
                    #self.playerChase.pop(int(dataArr[1]), None)
                    self.socket.sendto(f"DISCONNECT&{dataArr[1]}".encode(), addr)
                    login_socket = socket.socket()
                    login_socket.connect((servers_dict['login'][0], 6969))
                    login_socket.send(f"Disconnect%{dataArr[1]}".encode())
                    login_socket.close()

                if dataArr[0] == 'zDAMAGEWITCH':
                    # Example data: "gDAMAGEWITCH&witch_id&damage"
                    witch_id = int(dataArr[2])
                    damage_amount = int(dataArr[3])
                    self.handle_damage_witch(witch_id, damage_amount)
                if dataArr[0] == 'HI':
                    inv = f"sINV&{dataArr[1]}&{self.all_players[dataArr[1]]}"
                    self.socket.sendto(inv.encode(), addr)
                    print("Sending inv: ", inv)
                if dataArr[0] == 'gHELD':
                    ID_CLIENT = dataArr[1]
                    ITEM_HELD = dataArr[2]
                    stats = self.all_players[ID_CLIENT].split('&')
                    if ITEM_HELD == 'ak-47.png' and stats[1] != '0':
                        self.heldItems[ID_CLIENT] = ITEM_HELD
                    if ITEM_HELD == 'm4.png' and stats[2] != '0':
                        self.heldItems[ID_CLIENT] = ITEM_HELD
                    if ITEM_HELD == 'awp.png' and stats[3] != '0':
                        self.heldItems[ID_CLIENT] = ITEM_HELD
                    if ITEM_HELD == 'mp5.png' and stats[4] != '0':
                        self.heldItems[ID_CLIENT] = ITEM_HELD

                if dataArr[0] == 'gREMOVEITEM':
                    CHEST_ID = dataArr[1]
                    item = dataArr[2]
                    self.RemoveItemFromChest(CHEST_ID,item)

                if dataArr[0] == 'gPLAYERDEATH': #gPLAYERDEATH&x&y&z&item1&item2&...&item[n]
                    print("PLAYER DIED")
                    x = dataArr[2]
                    y = dataArr[3]
                    z = dataArr[4]
                    items = [dataArr[i] for i in range(5, len(dataArr))]
                    print(items)
                    self.GenerateChest(x,y,z,items)
                    # login_socket = socket.socket()
                    # login_socket.connect(("127.0.0.1", 6969))
                    # login_socket.send(f"Disconnect%{dataArr[1]}&{0}&{0}&{0}&{0}&{0}&{0}&{0}&{0}&{0}".encode())
                    # login_socket.close()
                if dataArr[0] == 'gREMOVECHEST':
                    self.RemoveChest(dataArr[1],dataArr[2])


            #except Exception as e:
            #    print(f"Error handling client: {e}")

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

# Example usage
if __name__ == "__main__":
    private_ip = get_private_ip()
    print (private_ip)
    serverNum = int(input("Enter server number: "))
    servers_dict[serverNum]=(private_ip ,12340+serverNum)   #put the server ip and port in dictionary
    serverAddress = servers_dict[serverNum]
    server = Server(serverAddress)

    ip=input("Fill the ip of the first server, if you already have done it, enter x")
    if ip!='x':
        servers_dict[1]=(ip,12341)

    ip = input("Fill the ip of the second server, if you already have done it, enter x")
    if ip != 'x':
        servers_dict[2] = (ip, 12342)

    ip = input("Fill the ip of the third server, if you already have done it, enter x")
    if ip != 'x':
        servers_dict[3] = (ip, 12343)

    ip = input("Fill the ip of the fourth server, if you already have done it, enter x")
    if ip != 'x':
        servers_dict[4] = (ip, 12344)

    ip = input ("Fill the ip of login-server")
    servers_dict['login'] = (ip, 6969)

    ip = input("Fill the ip of the load-balancer")
    LOAD_BALANCER_UDP_ADDR = (ip, 9999)





    server.start_server()