import customtkinter as ctk
from PIL import Image

# Selecting GUI theme - dark, light , system (for system default)
ctk.set_appearance_mode("dark")

# Selecting color theme - blue, green, dark-blue
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("500x500")
app.title("Sonis Ohel Batahat")


def login():
    return


def sign_in():
    return


logo = ctk.CTkImage(light_image=Image.open("GameLogo.png"),
                    dark_image=Image.open("GameLogo.png"),
                    size=(207, 134))

label1 = ctk.CTkLabel(app, text="", image=logo)
label1.pack(pady=12, padx=10)

frame = ctk.CTkFrame(master=app)
frame.pack(pady=20, padx=40, fill='both', expand=True)

user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
user_entry.pack(pady=12, padx=10)

user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
user_pass.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text='Login', command=login)
button.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text='Sign Up', command=sign_in)
button.pack(pady=12, padx=10)

app.mainloop()
