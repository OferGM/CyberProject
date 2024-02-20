import tkinter as tk
from tkinter import scrolledtext

def send_message():
    message = message_entry.get()
    if message:
        chat_display.configure(state='normal')
        chat_display.insert(tk.END, "You: " + message + "\n")
        chat_display.see(tk.END)
        chat_display.configure(state='disabled')
        message_entry.delete(0, tk.END)
    else:
        tk.messagebox.showwarning("Empty Message", "Please enter a message.")

# Create the main window
root = tk.Tk()
root.title("Chat Box")

# Create and place widgets in the window
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

# Chat Display (ScrolledText widget)
chat_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', height=15, width=40)
chat_display.pack(padx=10, pady=10)

# Message Entry and Send Button
message_entry = tk.Entry(frame, width=30)
message_entry.pack(padx=10, pady=5)

send_button = tk.Button(frame, text="Send", command=send_message)
send_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
