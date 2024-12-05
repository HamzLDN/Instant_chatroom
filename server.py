import socket
import threading

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'
USERNAME = b'\x40'

# Im going to be using a linked list for storing the client information

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

    def handle_client(self, client, username):
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    continue
                if bytes([data[0]]) == SEND_ALL:
                    self.send_all(username +data)
            except Exception as e:
                self.clients.remove(client)
                print("deleted", client)
                break
        print(self.clients)
        
    def recv_username(self, client):
        data = client.recv(20)
        print(data)
        if bytes([data[0]]) == USERNAME:
            print(data[1:].decode(), "Connected")
            return data[1:] + b": "

    def start_socket(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_sessions)
        print(f"Server is listening on {self.ip}:{self.port}")
        while True:
            client, address = self.socket.accept()
            self.clients.append(client)
            print(f"New connection from {address}")
            client.send(CONNECTED)
            username = self.recv_username(client)
            if username:
                threading.Thread(target=self.handle_client, args=(client,username,)).start()

server("localhost", 1234).start_socket()