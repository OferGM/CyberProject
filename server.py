import socket


class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = []
        self.coordinates = {}

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
            print(f"Server listening on {self.host}:{self.port}")
            self.accept_connections()
        except Exception as e:
            print(f"Error starting server: {e}")

    def accept_connections(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                print(f"Connected to {addr}")
                self.connections.append(addr)

                # Handle client data
                self.handle_client(data, addr)
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def handle_client(self, data, addr):
        try:
            # print(f"Received from client at {addr}: {data.decode()}")
            data = data.decode()
            dataArr = data.split('&')
            if dataArr[3] in self.coordinates:
                # If the key exists, update the existing entry
                self.coordinates[dataArr[3]] = (dataArr[0], dataArr[1], dataArr[2])
            else:
                # If the key doesn't exist, add a new entry
                self.coordinates[dataArr[3]] = (dataArr[0], dataArr[1], dataArr[2])
            print(self.coordinates)
            # Example: Echo back the received data to the client
            self.socket.sendto(data.encode(), addr)
        except Exception as e:
            print(f"Error handling client: {e}")


# Example usage
if __name__ == "__main__":
    server = Server()
    server.start_server()
