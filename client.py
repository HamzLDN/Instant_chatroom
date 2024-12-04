import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'

class ChatClient:
    def __init__(self, server_address='127.0.0.1', server_port=1234):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket = None
        self.root = tk.Tk()
        self.chat_display = None
        self.message_entry = None

    def recv_messages(self):
        """Receive messages from the server and display them in the chat."""
        while True:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    print(data)
                    message = data.decode('utf-8', errors='ignore')
                    self.display_message(message)
            except Exception as e:
                pass

    def display_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.client_socket.sendall(SEND_ALL + message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def run_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.server_address, self.server_port))
            print(f"Connected to server at {self.server_address}:{self.server_port}")
            threading.Thread(target=self.recv_messages, args=(), daemon=True).start()

            self.setup_gui()
            self.root.mainloop()

        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()

    def setup_gui(self):
        """ Setup the Tkinter GUI """
        self.root.title("Chatbox")
        self.chat_display = scrolledtext.ScrolledText(self.root, width=50, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10)

        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)

        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.grid(row=1, column=1, padx=10, pady=10)


if __name__ == "__main__":
    client = ChatClient() # put ur own address. Default is the loopback address with port 1234
    client.run_client()
