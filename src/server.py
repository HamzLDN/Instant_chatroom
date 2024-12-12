import socket
import threading
from src import tcp_enhancer
import json
import time

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'
USERNAME = b'\x40'
INVALID_USERNAME = b'\x50'
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
        return self.sort_chat(chatlogs)

    def sort_chat(self, chat):
        return "\n".join(chat.splitlines()[::-1])


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
        self.chatrooms = {'chatroom': {}}

    def send_all(self, message, roomID):
        for client in self.chatrooms['chatroom'][roomID]['clients']:
            self.coms.send(client, message)

    def forward_chat(self, client, username, roomID):
        data = self.coms.recv(client)
        if bytes([data[0]]) == SEND_ALL:
            self.chatrooms['chatroom'][roomID]['chat'].prepend((username + data[1:]).decode())
            self.send_all(SEND_ALL + username + data[1:], roomID)


    def handle_client(self, client, username, roomID):
        while True:
            try:
                self.forward_chat(client, username + b': ', roomID)
            except Exception as e:
                # if client is in the clients list then we delete
                if client in self.chatrooms['chatroom'][roomID]['clients']:
                    self.chatrooms['chatroom'][roomID]['clients'].remove(client)
                    self.chatrooms['chatroom'][roomID]['username_list'].remove(username)
        
    def recv_username(self, client):
        data = self.coms.recv(client)
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
                'clients': [],
                'username_list': []
            }
        
        # Validates the username by checking if it exists or not
        if username not in self.chatrooms['chatroom'][chatroom]['username_list']:
            self.chatrooms['chatroom'][chatroom]['username_list'].append(username)
        else:
            self.coms.send(client, INVALID_USERNAME)
            return

        if client not in self.chatrooms['chatroom'][chatroom]['clients']:
            self.chatrooms['chatroom'][chatroom]['clients'].append(client)

        room = self.chatrooms['chatroom'][chatroom]['chat']
        if username:
            self.coms.send(client, SEND_ALL+room.display_chatlogs().encode('utf-8')[1:20000])
            threading.Thread(target=self.handle_client, args=(client,username, chatroom)).start()
    
    def show_active_chatroom(self, _):
        # Bubblesort algorythm to find most to least active chatroom
        number_of_clients = []
        for x in self.chatrooms['chatroom'].keys():
            number_of_clients.append(len(self.chatrooms['chatroom'][x]['clients']))
        number_of_clients, roomID = self.bubblesort(number_of_clients, list(self.chatrooms['chatroom'].keys()))

        for i in range(len(number_of_clients)):
            print("="*20)
            print("Chatroom name   :  ", roomID[i])
            print("Number of people:",number_of_clients[i])
            print("="*20)
            

    def bubblesort(self, arr, chat):
        n = len(arr)
        for i in range(n-1):
            swapped = False
            for j in range(n-i-1):
                if arr[j] < arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    chat[j], chat[j+1] = chat[j+1], chat[j]
                    swapped = True
            if not swapped:
                break
        return arr, chat

    def list_chatrooms(self, _):
        print("CHATROOM LIST")
        for x in self.chatrooms['chatroom'].keys():
            print(x)
    
    def show_chatroom(self, roomID):
        print(self.chatrooms['chatroom'][" ".join(roomID[2:])]['chat'].display_chatlogs())

    def show_help(self, _):
        print("'list chatrooms' to show all available chatrooms")
        print("'show chatroom <id>' to view chatlogs")
        print("'show active' to view active chatlogs")

    def options(self):
        try:
            command = input("Command: ")
            args = command.strip().split()
            if not args:
                print("Command not provided. Type 'help' to view available commands.")
                return

            commands = {
                'help': self.show_help,
                'list chatrooms': self.list_chatrooms,
                'show chatroom': self.show_chatroom,
                'show active': self.show_active_chatroom,
            }

            #this willmatch and execute the command
            cmd_key = ' '.join(args[:2]) if len(args) > 1 else args[0]
            if cmd_key in commands:
                commands[cmd_key](args)
            else:
                print(f"Unknown command: {cmd_key}. Type 'help' for available commands.")

        except Exception as e:
            print(f"Error handling command: {e}")

    def console(self):
        print("You are now in the commandline Interface for the chatroom. Type help to see more options")
        while True:
            try: self.options()
            except Exception as e: print(e)

    def start_socket(self):
        # Binds the self.ip and self.port and listens up to 60 connections
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_sessions)
        print(f"Server is listening on {self.ip}:{self.port}")
        threading.Thread(target=self.console, args=()).start()
        while True:
            try:
                client, address = self.socket.accept()
                print(f"New connection from {address}")
                self.coms.send(client, CONNECTED)
                self.join_chat(client)
            except:
                time.sleep(1)

