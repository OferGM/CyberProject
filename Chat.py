import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

def receive():
    """ Handles receiving of messages from the server """
    while True:
        try:
            msg, _ = client_socket.recvfrom(1024)
            msg = msg.decode("utf8")
            chat_display.configure(state='normal')
            chat_display.insert(tk.END, msg + "\n")
            chat_display.see(tk.END)
            chat_display.configure(state='disabled')
        except OSError:
            break

def send_message():
    """ Sends messages entered into the entry field to the server """
    message = message_entry.get()
    if message:
        msg = f"gCHAT&{client_id}&{message}"
        print(msg)
        client_socket.sendto(msg.encode(), ADDR)
        message_entry.delete(0, tk.END)
    else:
        tk.messagebox.showwarning("Empty Message", "Please enter a message.")

def on_closing():
    """ This function is to be called when the window is closed. """
    client_socket.close()
    root.quit()

root = tk.Tk()
root.title("Chat Box")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

chat_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', height=15, width=40)
chat_display.pack(padx=10, pady=10)

message_entry = tk.Entry(frame, width=30)
message_entry.pack(padx=10, pady=5)

send_button = tk.Button(frame, text="Send", command=send_message)
send_button.pack(pady=10)

HOST = '127.0.0.1'  # Server's IP address
PORT = 12345  # Server's port
ADDR = (HOST, PORT)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_id = "User"  # You might want to create a unique way to identify this or let the user input their name

receive_thread = threading.Thread(target=receive)
receive_thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()