from socket import *
import time
import random
import struct


class Packet():
    def __init__(self, source_port, dest_port, seq_num, packet_type, data=None):
        self.source_port = int(source_port)
        self.dest_port = int(dest_port)
        self.seq_num = int(seq_num)
        self.packet_type = packet_type # 0 for probe, 1 for ACK
        if packet_type == 0:
            # if data is a string encode it
            if isinstance(data, str):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data.encode()

            # if data already in bytes keep it the same
            elif isinstance(data, bytes):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data

            else:
                raise ValueError(f"invalid data type for probe packet: {type(data)}")

        # data field empty for ACK packets
        elif packet_type == 1:
            self.data = None
        else:
            raise ValueError(f"invalid packet type: {packet_type}")

    def packet_to_bytes(self):
        # >: big endian
        # h: short = 16 bits ==> 2 bytes
        # i: int = 32 bits ==> 4 bytes
        # b: char = 8 bits ==> 1 byte

        # add data if it's a probe packet
        if self.packet_type == 0:
            data_val = self.data[0] if self.data else 0
            header = struct.pack(">bhhib", self.packet_type, self.source_port, self.dest_port, self.seq_num, data_val)
            return header

        header = struct.pack(">bhhib", self.packet_type, self.source_port, self.dest_port, self.seq_num, 0)

        return header

    def bytes_to_packet(data_bytes):

        if len(data_bytes) != 10:
            raise ValueError(f"Invalid packet length: {len(data_bytes)} bytes")

        packet_type, source_port, dest_port, seq_num, data_val = struct.unpack(">bhhib", data_bytes)

        # check packet types ==> if probe -> add data, if ack -> return
        if packet_type == 0:
            data = bytes([data_val])
            return Packet(source_port, dest_port, seq_num, 0, data)
        elif packet_type == 1:
            return Packet(source_port, dest_port, seq_num, 1, None)
        else:
            raise ValueError(f"unknown packet type: {packet_type}")


class Node():
    def __init__(self, ip, my_port, their_port, window_size=5):
        self.my_port = int(my_port)
        self.their_port = int(their_port)
        self.ip = (ip if ip is not None else "localhost")
        self.window_size = int(window_size)


    def run_receiver(self, p = 0.25):
        server_socket = socket(AF_INET, SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', self.my_port))
        expected_seq_num = 0

        print(f"Server on port {self.my_port} is set up!")
        # accept a connection
        while True:
            data, client_address = server_socket.recvfrom(1024)
            try:
                packet = Packet.bytes_to_packet(data)
                # intentionally drop every 4th packet
                if packet.packet_type == 0:
                    if random.random() < p:
                    # if packet.seq_num % 4 == 0:
                        print(f"Dropped packet {packet.seq_num}")
                        continue

                    # if we get the correct seq num, make new packet and send it to client socket
                    if packet.seq_num == expected_seq_num:
                        print(f"Recieved data: {packet.data.decode()} (seq num: {packet.seq_num})")
                        ack_packet = Packet(self.my_port, packet.source_port, packet.seq_num, 1)
                        server_socket.sendto(ack_packet.packet_to_bytes(), client_address)
                        expected_seq_num = expected_seq_num + 1

                    # otherwise we got a packet out of order so resend ACK of last ACK'd packet
                    else: 
                        if expected_seq_num > 0:
                            ack_packet = Packet(self.my_port, packet.source_port, expected_seq_num - 1, 1)
                            server_socket.sendto(ack_packet.packet_to_bytes(), client_address)
                            print(f"Out of order packet {packet.seq_num} sent ACK for {expected_seq_num - 1}")

            except Exception as e:
                print(f"Exception occured: {e}")


            # print(f"recieved from client: {sentence.decode()}")
            # capital_sentence = sentence.decode().upper()

            # server_socket.sendto(capital_sentence.encode(), client_address)

        server_socket.close()


    def run_sender(self):
        try:

            # AF_INET = internet address family for IPv4
            # SOCK_DGRAM = socket type for TCP
            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.bind(('0.0.0.0', self.my_port))
            client_socket.settimeout(5) # 500 ms timeout

            message = ['h', 'e', 'l', 'l', 'o', ' ', 't', 'h', 'e', 'r', 'e']

            next_seq_num = 0
            window_idx = 0

            print(f"Trying to connect to port {self.their_port}")

            timer = False
            timer_start_time = 0
            
            while window_idx < len(message):

                # send packets within window
                while next_seq_num < window_idx + self.window_size and next_seq_num < len(message):
                    print(f"sending packet {next_seq_num}, data={message[next_seq_num]}")
                    packet = Packet(self.my_port, self.their_port, next_seq_num, 0, message[next_seq_num])
                    client_socket.sendto(packet.packet_to_bytes(), (self.ip, self.their_port))
                    #print(f"sent packet {next_seq_num}, data={data[next_seq_num]}")
                    next_seq_num = next_seq_num + 1
                
                # start timer if not active and if there are unACK'd packets
                if not timer and window_idx < next_seq_num:
                    timer_start_time = time.time()
                    timer = True
                
                try:
                    data, server_address = client_socket.recvfrom(1024)
                    packet = Packet.bytes_to_packet(data)

                    if packet.packet_type == 1 and packet.seq_num >= window_idx:
                        window_idx = packet.seq_num + 1
                        print(f"received ACK {packet.seq_num}, window idx now {window_idx}")

                        # all sent packets are ACK'd
                        if window_idx == next_seq_num:
                            timer = False
                        else:
                            timer_start_time = time.time() # restart timer

                except TimeoutError:
                    if timer and time.time() - timer_start_time >= 0.5:
                        print(f"timeout at window idx: {window_idx}, resending window")

                        for seq in range(window_idx, next_seq_num):
                            packet = Packet(self.my_port, self.their_port, seq, 0, message[seq])
                            client_socket.sendto(packet.packet_to_bytes(), (self.ip, self.their_port))
                            print(f"resent packet {seq}")

                        timer_start_time = time.time()


            # client_socket.sendto(sentence.encode(), (self.ip, self.their_port))

            # modified_sentence, server_address = client_socket.recvfrom(1024)
            # print(f"from server: ", modified_sentence.decode())

            client_socket.close()

        except KeyboardInterrupt:
            print(f"Forced scanning to stop on port {self.their_port}")
            exit()
        # except socket.error:
            # print(f"{self.ip} not responding on port {self.their_port}")
            # exit()
    

