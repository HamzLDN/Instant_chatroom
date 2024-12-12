import socket, struct

class coms:
    def __init__(self):
        pass

    def send(self, sock, message):
        sock.sendall(struct.pack('>I', len(message)) + message)

    def recv(self, client_sock):
        msg_len = self.receive_all(client_sock, 4)
        if not msg_len: return None
        
        return self.receive_all(client_sock, struct.unpack('>I', msg_len)[0])

    def receive_all(self, client_sock, n):
        if n > 20000: return "CANNOT SEND DATA OVER 20,000 word length"
        data = bytearray()
        while len(data) < n:
            packet = client_sock.recv(n - len(data))
            if not packet: return None
            data.extend(packet)
        return data
