from socket import *
import struct


class Packet():
    def __init__(self, source_port, dest_port, seq_num, packet_type, data):
        self.source_port = int(source_port)
        self.dest_port = int(dest_port)
        self.seq_num = int(seq_num)
        self.packet_type = packet_type # 0 for probe, 1 for ACK
        self.data = data

    def packet_to_bytes(self):
        # >: big endian
        # h: short = 16 bits ==> 2 bytes
        # i: int = 32 bits ==> 4 bytes
        # b: char = 8 bits ==> 1 byte
        header = struct.pack(">bhhi", self.packet_type, self.source_port, self.dest_port, self.seq_num)

        # add data if it's a probe packet
        if self.packet_type == 0:
            header = header + self.data

        return header

    def bytes_to_packet(data):

        source_port, dest_port, seq_num, packet_type = struct.unpack(">bhhi", data[:9])

        # check packet types ==> if probe -> add data, if ack -> return
        if packet_type == 0:
            return Packet(source_port, dest_port, seq_num, 0, data[9:10])
        elif packet_type == 1:
            return Packet(source_port, dest_port, seq_num, 0, None)
        else:
            raise ValueError("unknown packet type")


class Node():
    def __init__(self, ip, my_port, their_port, window_size=5):
        self.my_port = int(my_port)
        self.their_port = int(their_port)
        self.ip = (ip if ip is not None else "localhost")
        self.window_size = int(window_size)


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

