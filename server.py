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