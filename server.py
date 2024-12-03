import socket
import threading

class server:
    def __init__(self, ip:str,port:int, max_sessions=3) -> None:
        self.ip = ip
        self.port = port
        self.max_sessions = max_sessions
        self.socket = socket.socket()
        self.clients = []

    def start_socket(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_sessions)
        while True:
            client, address = self.socket.accept()
            self.clients.append(client)
            print(f"New connection from {address}")
            threading.Thread(target=self.handle_client, args=(client,)).start()


server("0.0.0.0", 1234).start_socket()
