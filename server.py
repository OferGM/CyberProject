import random
import socket
import threading
import time

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
        self.items = {}

    def GenerateMobs(self):
        if len(self.mobs) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = [
            random.randint(1, 50), 1, random.randint(1, 50), random.randint(0, 360)]
            self.mobs[id] = random_coordinates

    def GenerateItem(self,x,z):
        id = random.randint(10000000, 99999999)
        random_coordinates = [x, 1, z, random.randint(0, 360)]
        self.items[id] = random_coordinates

    def CreateMobString(self):
        print(len(self.mobs))
        mob_strings = ["aM&"]
        for id, coords in self.mobs.items():
            # Format each mob's data into "id&x&y&z"
            mob_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&"
            mob_strings.append(mob_str)
        # Join all mob strings into one single string, separated by semicolons
        all_mobs_string = ";".join(mob_strings)
        return all_mobs_string

    def CreateItemString(self):
        item_strings = ["aI&"]
        for id, coords in self.items.items():
            # Format each mob's data into "id&x&y&z"
            item_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&"
            item_strings.append(item_str)
        # Join all mob strings into one single string, separated by semicolons
        all_items_string = ";".join(item_strings)
        return all_items_string

    def SendPositions(self, addr):
        print("sending")
        data = self.CreateMobString()
        self.socket.sendto(data.encode(), addr)
        data = self.CreateItemString()
        self.socket.sendto(data.encode(), addr)

    def start_server(self):
        try:
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()
            self.GenerateMobs()

            self.socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")
            threading.Thread(target=self.update_zombies).start()
            threading.Thread(target=self.handle_client).start()
            print(len(self.mobs))
        except Exception as e:
            print(f"Error starting server: {e}")

    def update_positions(self):
        for zombie_id in self.mobs.keys():
            self.mobs[zombie_id][0] += 1

    def update_zombies(self):
        while(True):
            if (len(self.mobs) < 10):
                self.GenerateMobs()
            self.update_positions()
            self.SendPositions(addr=LOAD_BALANCER_UDP_ADDR)
            time.sleep(0.5)

    def handle_client(self):
        while(True):
            try:
                data, addr = self.socket.recvfrom(4096)
                data = data.decode()
                print(data)
                dataArr = data.split('&')
                if dataArr[0] == 'gSTATE':
                    msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}'
                    self.socket.sendto(msg.encode(), addr)
                if dataArr[0] == 'gDEAD':
                    self.GenerateItem(self.mobs[int(dataArr[2])][0],self.mobs[int(dataArr[2])][2])
                    self.mobs.pop(int(dataArr[2]))
                if dataArr[0] == 'gPICKED':
                    self.items.pop(int(dataArr[2]))

            except Exception as e:
                print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()