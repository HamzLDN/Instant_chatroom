import socket
import threading
import tcp_enhancer
import json

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'
USERNAME = b'\x40'

class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next_node = next_node

class LinkedList:
    def __init__(self, value=None):
        self.head_node = Node(value)
    
    def prepend(self, new_data):
        new_node = Node(new_data)
        new_node.next_node = self.head_node
        self.head_node = new_node
    
    def display_chatlogs(self):
        chatlogs = ""
        current_node = self.head_node
        while current_node:
            if current_node.value != None:
                chatlogs += str(current_node.value) + "\n"
            current_node = current_node.next_node
        return chatlogs
        

# Im going to be using a linked list for storing the client information

# Each id will have its own chatroom
class server:
    def __init__(self, ip:str,port:int, max_sessions=60) -> None:
        self.ip = ip
        self.port = port
        self.max_sessions = max_sessions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.coms = tcp_enhancer.coms()
        self.chatlogs = LinkedList(None)
        self.chatrooms = {
            'chatroom': {
                1: {
                    'chat': LinkedList(None),
                    'clients': []
                }
            }
        }

    def send_all(self, message, roomID):
        print(self.chatrooms['chatroom'][roomID]['clients'])
        for client in self.chatrooms['chatroom'][roomID]['clients']:
            self.coms.send(client, message)

    def forward_chat(self, client, username, roomID):
        data = self.coms.recv(client)
        if bytes([data[0]]) == SEND_ALL:
            self.chatrooms['chatroom'][roomID]['chat'].prepend((username + data[1:]).decode())
            self.send_all(SEND_ALL + username + data, roomID)


    def remove_clients(self, client):
        self.clients.remove(client)
        print("deleted", client)
        client.close()

    def handle_client(self, client, username, chatroom):
        while True:
            try:
                self.forward_chat(client, username, chatroom)
            except Exception as e:
                pass
                
        print(self.clients)
        
        
    def recv_username(self, client):
        data = self.coms.recv(client)
        print(data)
        if bytes([data[0]]) == USERNAME:
            data = json.loads(data[1:])
            return data['username'].encode('utf-8'), data['chatroom']
        else:
            return False

    def join_chat(self, client):
        username, chatroom = self.recv_username(client)
        if chatroom not in self.chatrooms['chatroom']:
            self.chatrooms['chatroom'][chatroom] = {
                'chat': LinkedList(None),
                'clients': []
            }
        print(self.chatrooms)
        if client not in self.chatrooms['chatroom'][chatroom]['clients']:
            self.chatrooms['chatroom'][chatroom]['clients'].append(client)

        room = self.chatrooms['chatroom'][chatroom]['chat']
        if username:
            self.coms.send(client, SEND_ALL+room.display_chatlogs()[:-1].encode('utf-8'))
            threading.Thread(target=self.handle_client, args=(client,username + b": ", chatroom)).start()
            

    def start_socket(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_sessions)
        print(f"Server is listening on {self.ip}:{self.port}")
        while True:
            client, address = self.socket.accept()
            print(f"New connection from {address}")
            self.coms.send(client, CONNECTED)
            self.join_chat(client)

server = server("localhost", 1234)
server.start_socket()