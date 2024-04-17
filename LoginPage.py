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
        print("sending")
        client_sock.send(response.encode())
        data = client_sock.recv(1024).decode()
        print("reciving")
        if data == "Login_failed":
            customtkinter.CTkInputDialog(text="INVALID INPUT\n WRONG USERNAME OR PASSWORD\nWrite feedback below:",
                                         title="sonis faggot")

        if data == "Login_successful":
            close_page()


    else:
        customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN "
                                          "% OR &. \nWrite feedback below:", title="sonis faggot")

    return


def sign_in(client_sock, username, password):
    if all(char not in (username + password) for char in "%&") and username and password:
        response = f"Sign_in%{username}&{password}"
        client_sock.send(response.encode())
        data = client_sock.recv(1024).decode()
        if data == "Taken":
            customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME TAKEN\nWrite feedback below:",
                                         title="sonis faggot")

        if data == "Sign_in_successful":
            print("signed in")
            close_page()

    else:
        customtkinter.CTkInputDialog(text="INVALID INPUT\n USERNAME AND PASSWORD MUST NOT BE EMPTY OR CONTAIN "
                                          "% OR &. \nWrite feedback below:", title="sonis faggot")
        return


def close_page():
    app.destroy()


def main(client_sock):
    build_page(client_sock)


if __name__ == "__main__":
    main(1)
