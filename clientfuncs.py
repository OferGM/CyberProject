import socket
import random


class clientfuncs:
    def __init__(self):
        self.server_address = ('localhost', 12345)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False
        self.id =  random.randint(1, 10**8)

    def send_data(self, data):
        try:
            self.socket.sendto(data.encode(), self.server_address)
        except Exception as e:
            print(f"Failed to send data to server: {e}")

    def receive_data(self):
        try:
            data, server = self.socket.recvfrom(1024)  # Adjust buffer size as needed
            # Process received data
            print("Received data from server:", data.decode())  # Deserialize received data
            data = data.decode()
            dataArr = data.split('&')


        except Exception as e:
            print(f"Failed to receive data from server: {e}")



# Example usage
if __name__ == "__main__":
    client = clientfuncs()
    # Send data to the server
    client.send_data("Hello, server!")
    # Receive data from the server
    client.receive_data()
