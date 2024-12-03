import socket
import threading

SEND_ALL = b'\x10'
MESSAGE = b'\x20'
CONNECTED = b'\x30'

class server:
    def __init__(self, ip:str,port:int, max_sessions=3) -> None:
        self.ip = ip
        self.port = port
        self.max_sessions = max_sessions
        self.socket = socket.socket()
        self.clients = []

    def send_all(self, message):
        for client in self.clients:
            client.send(message.encode())

    def handle_client(self, client):
        while True:
            print(client.recv(4096))

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