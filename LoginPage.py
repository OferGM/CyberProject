import customtkinter
import customtkinter as ctk
import socket
from functools import partial
import pygame
from pygame import mixer
from PIL import Image

app = ctk.CTk()


def build_page(client_sock):
    pygame.init()
    mixer.music.load('MyNig.mp3')
    mixer.music.play()

    # Selecting GUI theme - dark, light , system (for system default)
    ctk.set_appearance_mode("dark")

    # Selecting color theme - blue, green, dark-blue
    ctk.set_default_color_theme("green")

    app.geometry("500x500")
    app.resizable(False, False)
    app.title("Sonis Ohel Batahat")

    logo = ctk.CTkImage(light_image=Image.open("GameLogo.png"),
                        dark_image=Image.open("GameLogo.png"),
                        size=(207, 134))

    label1 = ctk.CTkLabel(app, text="", image=logo)
    label1.pack(pady=12, padx=10)

    frame = ctk.CTkFrame(master=app)
    frame.pack(pady=20, padx=40, fill='both', expand=True)

    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
    user_entry.pack(pady=12, padx=10)

    pass_entry = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    pass_entry.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text='Login',
                           command=lambda: login(client_sock, user_entry.get(), pass_entry.get()))
    button.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text='Sign Up',
                           command=lambda: sign_in(client_sock, user_entry.get(), pass_entry.get()))
    button.pack(pady=12, padx=10)

    app.mainloop()


def login(client_sock, username, password):
    if all(char not in (username + password) for char in "%&") and username and password:
        response = f"Login%{username}&{password}"
        print("Sending login request: ", response)
        client_sock.send(encrypt(response))
        data = client_sock.recv(9192)
        data = decrypt(data)
        print("Received: ", data)
        if data == "Login_failed":
            print("Login failed, wrong username or password")
            customtkinter.CTkInputDialog(text="INVALID INPUT\n WRONG USERNAME OR PASSWORD\nWrite feedback below:",
                                         title="sonis faggot")

        if data == "User_already_connected":
            print("Login failed, user already connected")
            customtkinter.CTkInputDialog(text="USER ALREADY CONNECTED\nWrite feedback below:",
                                         title="sonis faggot")

        if data == "Login_successful":
            print("Login successful")
            close_page()


    else:
        print("Invalid input, USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN % OR &")
        customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN "
                                          "% OR &. \nWrite feedback below:", title="sonis faggot")

    return


def sign_in(client_sock, username, password):
    if all(char not in (username + password) for char in "%&") and username and password:
        response = f"Sign_in%{username}&{password}"
        client_sock.send(encrypt(response))
        print("Sending sign in request: ", response)
        data = client_sock.recv(9192)
        data = decrypt(data)
        print("Received: ", data)
        if data == "Taken":
            print("Sign in failed, username already taken")
            customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME TAKEN\nWrite feedback below:",
                                         title="sonis faggot")

        if data == "Sign_in_successful":
            print("Sign in successful")
            close_page()
            sys.exit()

    else:
        print("Invalid input, USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN % OR &")
        customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN "
                                          "% OR &. \nWrite feedback below:", title="sonis faggot")
        return


def close_page():
    socket1.close()
    print("Socket closed")
    app.destroy()


def encrypt(data):
    # Convert message and key to byte arrays
    message_bytes = data.encode('ascii', 'ignore')
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the message and the key
    encrypted_bytes = bytes([message_byte ^ key_byte for message_byte, key_byte in zip(message_bytes, key_bytes)])
    poo = f"{client_id}&".encode('ascii', 'ignore')
    encrypted_bytes = poo + encrypted_bytes
    print("encrypted bytes: ", encrypted_bytes)
    return encrypted_bytes


def decrypt(data):
    # Convert key to bytes (using 4 bytes and little endian byteorder)
    key_bytes = shared_key.to_bytes(1024, byteorder='little')

    # Perform XOR operation between each byte of the encrypted message and the key
    decrypted_bytes = bytes([encrypted_byte ^ key_byte for encrypted_byte, key_byte in zip(data, key_bytes)])
    # Convert the decrypted bytes back to a string
    decrypted_message = decrypted_bytes.decode('ascii', 'ignore')

    return decrypted_message


if __name__ == "__main__":
    import sys

    socket1 = socket.socket()
    print("Parameter gotten is: ", sys.argv[1])
    print("Shared key is: ", sys.argv[2])
    socket1.bind((sys.argv[4], int(sys.argv[1])))
    client_id = int(sys.argv[1])
    shared_key = int(sys.argv[2])
    print(str(sys.argv[3]))
    socket1.connect((str(sys.argv[3]), 6969))
    build_page(socket1)
    print("Finished with login page")
    socket1.close()
    exit()
