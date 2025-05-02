from socket import *
import struct

class Node():
    def __init__(self, ip, my_port, their_port):
        self.my_port = int(my_port)
        self.their_port = int(their_port)
        self.ip = (ip if ip is not None else "localhost")


    def accept_connection(self):
        server_socket = socket(AF_INET, SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', self.my_port))

        print(f"Server on port {self.my_port} is set up!")
        # accept a connection
        while True:
            sentence, client_address = server_socket.recvfrom(1024)

            print(f"recieved from client: {sentence.decode()}")
            capital_sentence = sentence.decode().upper()

            server_socket.sendto(capital_sentence.encode(), client_address)

        conn.close()


    def connect_port(self):
        try:
            print(f"Trying to connect to port {self.their_port}")

            # AF_INET = internet address family for IPv4
            # SOCK_DGRAM = socket type for TCP
            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.settimeout(5)

            sentence = "hello there"
            client_socket.sendto(sentence.encode(), (self.ip, self.their_port))

            modified_sentence, server_address = client_socket.recvfrom(1024)
            print(f"from server: ", modified_sentence.decode())

            client_socket.close()           

        except KeyboardInterrupt:
            print(f"Forced scanning to stop on port {self.their_port}")
            exit()
        # except socket.error:
            # print(f"{self.ip} not responding on port {self.their_port}")
            # exit()
    
        return True

