import socket
import random


class clientfuncs:
    def __init__(self, client_id, lb_ip):
        self.server_address = (lb_ip, 9999)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((lb_ip, 9999))
        self.connected = False
        self.id = client_id

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.socket.getsockname()

    def send_data(self, data):
        try:
            self.socket.sendto(data, self.server_address)
        except Exception as e:
            pass

    def receive_data(self):
        try:
            data, server = self.socket.recvfrom(9192)  # Adjust buffer size as needed
            # Process received data
            if data == b'':
                return
            #data = data.decode()
            return data
        except socket.timeout:
            pass
            # Handle the lack of data here, such as setting a default value or raising an error
            # For example:
            # dataArr = []
            # or
            # raise Exception("No data received within timeout period")
        except Exception as e:
            pass

        except Exception as e:
            pass



# Example usage
if __name__ == "__main__":
    client = clientfuncs()
    # Send data to the server
    client.send_data("Hello, server!")
    # Receive data from the server
    client.receive_data()
