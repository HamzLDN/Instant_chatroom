from src.server import server

server = server("0.0.0.0", 1234)
server.start_socket()