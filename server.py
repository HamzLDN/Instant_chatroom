import socket
import threading

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'


class server:
    def __init__(self, ip:str,port:int, max_sessions=3) -> None:
        self.ip = ip
        self.port = port
        self.max_sessions = max_sessions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []

    def send_all(self, message):
        for client in self.clients:
            client.send(message)

    def handle_client(self, client):
        while True:
            data = client.recv(4096)
            
            if data:
                print(bytearray(data))
                print(len(data))
            if bytes([data[0]]) == SEND_ALL:
                print(data)
                self.send_all(data)

    def start_socket(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_sessions)
        while True:
            client, address = self.socket.accept()
            self.clients.append(client)
            print(f"New connection from {address}")
            client.send(CONNECTED)
            threading.Thread(target=self.handle_client, args=(client,)).start()

server("localhost", 1234).start_socket()

# import os
# import sys
# import shutil

# def fixed_input_ui():
#     os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal at start
#     terminal_size = shutil.get_terminal_size()
#     terminal_height = terminal_size.lines
#     input_position = (terminal_height - 2, 5)  # Fixed input near the bottom
#     max_output_lines = terminal_height - 3  # Leave space for input and prompt
#     output_lines = []  # Store printed lines

#     try:
#         while True:
#             # Clear the input line and move the cursor
#             sys.stdout.write(f"\033[{input_position[0]};0H\033[K")
#             sys.stdout.write(f"\033[{input_position[0]};{input_position[1]}H")
#             sys.stdout.write("Input: ")  # Display prompt
#             sys.stdout.flush()

#             # Read user input
#             user_input = input()  # Cursor remains fixed here

#             # Add the new line to the output buffer
#             output_lines.append(f"You typed: {user_input}")

#             # Keep only the last `max_output_lines` to avoid scrolling
#             if len(output_lines) > max_output_lines:
#                 output_lines.pop(0)

#             # Redraw output lines
#             for i, line in enumerate(output_lines):
#                 sys.stdout.write(f"\033[{i+1};0H\033[K")  # Clear line
#                 sys.stdout.write(line + '\n')
            
#             sys.stdout.flush()
#     except KeyboardInterrupt:
#         print("\nExiting...")


# fixed_input_ui()