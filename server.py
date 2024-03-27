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
            self.SendInfo()  # Call SendInfo to start sending updates
            self.accept_connections()
            print(len(self.mobs))
        except Exception as e:
            print(f"Error starting server: {e}")

    def accept_connections(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                # print(f"Connected to {addr}")
                self.connections.append(addr)

                # Handle client data
                self.handle_client(data, addr)
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def SendInfo(self):
        def repeat_send():
            while True:
                i = 0
                for key in self.coordinates:
                    self.SendPositions(key,self.connections[i])
                    i+=1
                time.sleep(0.1)  # Wait for 0.3 seconds before sending the next update

        # Start the repeat_send function in a new thread
        threading.Thread(target=repeat_send).start()

    def handle_client(self, data, addr):
        try:
            data = data.decode()
            print(data)
            dataArr = data.split('&')
            if dataArr[0] == "R":
                if int(dataArr[1]) in self.mobs:
                    print(f"Removed zombie: {dataArr[1]}")
                    self.mobs.pop(int(dataArr[1]))
                    return
                print("NOT REMOVED")
                return
            if dataArr[1] == "disconnect":
                self.connections.remove(addr)
                self.disconnected.append(dataArr[0])
                print(f"{dataArr[0]} disconnected")
                self.coordinates.pop(dataArr[0])
                return

            if dataArr[4] in self.coordinates:
                # If the key exists, update the existing entry
                self.coordinates[dataArr[4]] = (dataArr[0], dataArr[1], dataArr[2], dataArr[3])
            elif not dataArr[4] in self.disconnected:
                print("NEW USER")
                # If the key doesn't exist, add a new entry
                self.coordinates[dataArr[4]] = (dataArr[0], dataArr[1], dataArr[2], dataArr[3])
            # Example: Echo back the received data to the client

        except Exception as e:
            print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()
