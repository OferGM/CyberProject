import tkinter as tk
from tkinter import messagebox

def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    # For demonstration purposes, check if the username and password are not empty
    if entered_username and entered_password:
        quit()
    else:
        messagebox.showwarning("Login Failed", "Please enter both username and password.")

# Create the main window
root = tk.Tk()
root.title("Login Page")

# Create and place widgets in the window
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

# Username Label and Entry
username_label = tk.Label(frame, text="Username:")
username_label.grid(row=0, column=0, sticky="e")

username_entry = tk.Entry(frame)
username_entry.grid(row=0, column=1, padx=10, pady=10)

# Password Label and Entry
password_label = tk.Label(frame, text="Password:")
password_label.grid(row=1, column=0, sticky="e")

password_entry = tk.Entry(frame, show="*")  # Show asterisks for password
password_entry.grid(row=1, column=1, padx=10, pady=10)

# Login Button
login_button = tk.Button(frame, text="Login", command=login)
login_button.grid(row=2, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
