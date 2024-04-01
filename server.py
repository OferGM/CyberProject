import random
import socket
import threading
import time

class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = []
        self.coordinates = {}
        self.disconnected = []
        self.mobs = {}

    def GenerateMobs(self):
        if len(self.mobs) < 10:
            id = random.randint(10000000, 99999999)
            random_coordinates = (
            random.randint(1, 50), 0, random.randint(1, 50), random.randint(0, 360))
            self.mobs[id] = random_coordinates

    def CreateMobString(self):
        print(len(self.mobs))
        mob_strings = ["M"]
        for id, coords in self.mobs.items():
            # Format each mob's data into "id&x&y&z"
            mob_str = f"{id}&{coords[0]}&{coords[1]}&{coords[2]}&"
            mob_strings.append(mob_str)
        # Join all mob strings into one single string, separated by semicolons
        all_mobs_string = ";".join(mob_strings)
        return all_mobs_string

    def SendPositions(self, id, addr):
        for key in self.coordinates:
            if len(self.coordinates) == 1 and key == id:
                data = "Single"
                self.socket.sendto(data.encode(), addr)
                MobData = self.CreateMobString()
                if MobData != "M":
                    print(MobData)
                    self.socket.sendto(MobData.encode(), addr)
            if key != id:
                print(id, type(id))
                coords = self.coordinates[key]
                data = f"{coords[0]}&{coords[1]}&{coords[2]}&{coords[3]}&{coords[4]}"
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
            threading.Thread(target=self.handle_client).start()
            print(len(self.mobs))
        except Exception as e:
            print(f"Error starting server: {e}")

    def handle_client(self):
        while(True):
            try:
                data, addr = self.socket.recvfrom(4096)
                data = data.decode()
                dataArr = data.split('&')
                if dataArr[0] == 'gSTATE':
                    msg = f'STATE&{dataArr[1]}&{dataArr[2]}&{dataArr[3]}&{dataArr[4]}&{dataArr[5]}'
                    self.socket.sendto(msg.encode(), addr)

            except Exception as e:
                print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()
