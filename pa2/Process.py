from socket import *
import struct

class Node():
    def __init__(self, ip, my_port, their_port):
        self.my_port = int(my_port)
        self.their_port = int(their_port)
        self.ip = (ip if ip is not None else "localhost")


    def accept_connection(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.my_port))
        server_socket.listen(1)

        print(f"Server on port {self.my_port} is listening!")

        # accept a connection
        while True:
            conn, addr = server_socket.accept()
            sentence = conn.recv(1024).decode()
            print(f"from client: {sentence}")
            capital_sentence = sentence.upper()

            conn.send(capital_sentence.encode())
            conn.close()

            # data = conn.recv(1024) # window size?
            # if not data:
                # break
            # con.sendall(data)


    def connect_port(self):
        try:
            print(f"Trying to connect to port {self.their_port}")

            # AF_INET = internet address family for IPv4
            # SOCK_STREAM = socket type for TCP
            client_socket = socket(AF_INET, SOCK_STREAM)
            client_socket.settimeout(5)

            result = client_socket.connect_ex((self.ip, self.their_port))
            if result == 0:
                sentence = "hello there"
                # service = socket.getservbyport(self.their_port, 'tcp')
                # print(f"Found service {service} for port {self.their_port}")
                client_socket.send(sentence.encode())

                modified_sentence = client_socket.recv(1024)
                print(f"from server: ", modified_sentence.decode())

            client_socket.close()           

        except KeyboardInterrupt:
            print(f"Forced scanning to stop on port {self.their_port}")
            exit()
        # except socket.error:
            # print(f"{self.ip} not responding on port {self.their_port}")
            # exit()
    
        return True

