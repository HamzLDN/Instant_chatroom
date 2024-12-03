import socket
import threading

SEND_ALL = b'\x10'
DIRECT_MESSAGE = b'\x20'
CONNECTED = b'\x30'


def recv_messages(socket):
    while True:
        print(socket.recv(4096))
def run_client():
    server_address = '127.0.0.1'
    server_port = 1234

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_address, server_port))
        print(f"Connected to server at {server_address}:{server_port}")
        threading.Thread(target=recv_messages, args=(client_socket,)).start()
        while True:
            message = input("Send message: ")
            client_socket.sendall(SEND_ALL+message.encode('utf-8'))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_client()
