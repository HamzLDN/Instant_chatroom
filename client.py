import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'


def recv_messages(client_socket, text_widget):
    """Receives messages and appends them to the tkinter Text widget."""
    while True:
        try:
            data = client_socket.recv(4096)
            if data:
                text_widget.insert(tk.END, f"Server: {data.decode('utf-8')}\n")
                text_widget.yview(tk.END)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


def send_message(client_socket, message):
    """Send the message to the server."""
    client_socket.sendall(SEND_ALL + message.encode('utf-8'))


def run_client(text_widget, entry_widget):
    """Main client logic with tkinter integration."""
    server_address = '127.0.0.1'
    server_port = 1234

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_address, server_port))
        print(f"Connected to server at {server_address}:{server_port}")

        threading.Thread(target=recv_messages, args=(client_socket, text_widget), daemon=True).start()

        while True:
            # get the message from tkinter
            message = entry_widget.get()
            if message:
                send_message(client_socket, message)
                entry_widget.delete(0, tk.END)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()


def create_gui():
    """Create the GUI using tkinter."""
    window = tk.Tk()
    window.title("Client Chat")
    text_widget = scrolledtext.ScrolledText(window, width=50, height=20, wrap=tk.WORD, state=tk.DISABLED)
    text_widget.grid(row=0, column=0, padx=10, pady=10)
    entry_widget = tk.Entry(window, width=40)
    entry_widget.grid(row=1, column=0, padx=10, pady=10)
    send_button = tk.Button(window, text="Send", width=20, command=lambda: send_message(client_socket, entry_widget.get()))
    send_button.grid(row=1, column=1, padx=10, pady=10)
    threading.Thread(target=run_client, args=(text_widget, entry_widget), daemon=True).start()
    window.mainloop()


if __name__ == "__main__":
    create_gui()
