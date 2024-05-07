import socket
import requests
import random


def get_ip_address():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a remote server (doesn't matter which one)
        s.connect(("8.8.8.8", 80))

        # Get the socket's local address, which is the local IP address
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Error getting IP address: {e}")
        ip_address = None
    finally:
        # Close the socket
        s.close()

    return ip_address


class clientfuncs:
    def __init__(self, client_id):
        self.server_address = ("172.31.160.1", 9999)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("172.31.160.1", 9999))
        self.connected = False
        self.id = client_id

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.socket.getsockname()

    def send_data(self, data):
        try:
            self.socket.sendto(data.encode(), self.server_address)
        except Exception as e:
            print(f"Failed to send data to server: {e}")

    def receive_data(self):
        try:
            data, server = self.socket.recvfrom(9192)  # Adjust buffer size as needed
            # Process received data
            if data == b'':
                return
            data = data.decode()
            return data
        except socket.timeout:
            print("No data received within timeout period")
            # Handle the lack of data here, such as setting a default value or raising an error
            # For example:
            # dataArr = []
            # or
            # raise Exception("No data received within timeout period")
        except Exception as e:
            print("An error occurred:", e)


        except Exception as e:
            print(f"Failed to receive data from server: {e}")


# Example usage
if __name__ == "__main__":
    client = clientfuncs()
    # Send data to the server
    client.send_data("Hello, server!")
    # Receive data from the server
    client.receive_data()
