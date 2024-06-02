import socket
import threading
import tkinter as tk
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 57687


class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("UDP Chat Room")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 0))  # Binds to localhost with a system-assigned port
        self.server_address = (HOST, PORT)

        self.text_area = tk.Text(master)
        self.text_area.pack(padx=20, pady=20)

        self.msg_entry = tk.Entry(master)
        self.msg_entry.pack(padx=20, pady=20)
        self.msg_entry.bind("<Return>", self.send_message)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event):
        message = self.msg_entry.get()
        self.socket.sendto(message.encode(), self.server_address)
        self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            message, _ = self.socket.recvfrom(1024)
            self.text_area.insert(tk.END, f"{message.decode()}\n")


def ClientChat():
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()