from socket import *
import time
import random
import threading
import struct

from Packet import Packet

class Node():
    def __init__(self, ip, my_port, send_ports, recv_ports, window_size=5):
        self.my_port = int(my_port)
        self.send_ports = send_ports
        self.recv_ports = recv_ports
        
        self.ip = (ip if ip is not None else "localhost")
        self.window_size = int(window_size)

        # create and bind one UDP socket for node
        self.recv_socket = socket(AF_INET, SOCK_DGRAM)
        self.recv_socket.bind(('0.0.0.0', self.my_port))

        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.send_socket.bind(('0.0.0.0', 0))
        
        self.send_port = int(self.send_socket.getsockname()[1])
        self.send_socket.settimeout(0.5) # timeout at 5s so doesn't globble chat
        
        # broadcasting to fire other senders
        self.peers = set(self.send_ports) | { port for (port,_) in self.recv_ports }
        self.start_event = threading.Event()

    
    def broadcast_start(self):
        print(f"[{self.my_port}] broadcasting START to {sorted(self.peers)}")
        for peer in self.peers:
            packet = Packet(self.send_port, peer, 0, 2) # send start packet
            self.send_socket.sendto(packet.packet_to_bytes(), (self.ip, peer))


    def run_receiver(self, port, p = 0.25):
        recv_socket = self.recv_socket
        expected_seq_num = 0

        # print(f"receiver on port {self.my_port} is set up!")
        # accept a connection
        print(f"[recv on {self.my_port}] starting, drop_p={p}")
        while True:
            data, client_address = recv_socket.recvfrom(1024)
            try:
                packet = Packet.bytes_to_packet(data)
                # intentionally drop every 4th packet

                # if broadcast packet comes in and no thread running
                if packet.packet_type == 2 and not self.start_event.is_set():
                    print(f"[{self.my_port}] got GLOBAL START from {client_address[1]}")

                    # immediately re-broadcast to all neighbors
                    self.broadcast_start()

                    # wake up the main thread
                    self.start_event.set()
                    continue
                
                if packet.packet_type == 0:
                    if random.random() < p:
                    # if packet.seq_num % 4 == 0:
                        # print(f"Dropped packet {packet.seq_num}")
                        print(f"[recv:{port}] dropped seq={packet.seq_num}")
                        continue

                    # if we get the correct seq num, make new packet and send it to client socket
                    if packet.seq_num == expected_seq_num:
                        print(f"[recv:{port}] {packet.data.decode()} (seq num: {packet.seq_num})")
                        ack_packet = Packet(self.my_port, packet.source_port, packet.seq_num, 1)
                        recv_socket.sendto(ack_packet.packet_to_bytes(), client_address)
                        expected_seq_num = expected_seq_num + 1

                    # otherwise we got a packet out of order so resend ACK of last ACK'd packet
                    else: 
                        if expected_seq_num > 0:
                            ack_packet = Packet(self.my_port, packet.source_port, expected_seq_num - 1, 1)
                            recv_socket.sendto(ack_packet.packet_to_bytes(), client_address)
                            print(f"[recv:{port}] Out of order packet {packet.seq_num} sent re-ACK for {expected_seq_num - 1}")

            except TimeoutError as e:
                print(f"Reciever timed out, trying again")
            except Exception as e:
                print(f"Exception occured: {e}")


            # print(f"recieved from client: {sentence.decode()}")
            # capital_sentence = sentence.decode().upper()

            # recv_socket.sendto(capital_sentence.encode(), client_address)

        recv_socket.close()


    def run_sender(self, dest_port):
        try:
            send_socket = self.send_socket
            send_port = self.send_port
            message = ['h', 'e', 'l', 'l', 'o', ' ', 't', 'h', 'e', 'r', 'e']

            next_seq_num = 0
            window_idx = 0

            print(f"Trying to connect to port {dest_port}")

            timer = False
            timer_start_time = 0
            
            while window_idx < len(message):

                # send packets within window
                while next_seq_num < window_idx + self.window_size and next_seq_num < len(message):
                    print(f"sending packet {next_seq_num}, data={message[next_seq_num]}")
                    packet = Packet(self.send_port, dest_port, next_seq_num, 0, message[next_seq_num])
                    send_socket.sendto(packet.packet_to_bytes(), (self.ip, dest_port))
                    #print(f"sent packet {next_seq_num}, data={data[next_seq_num]}")
                    next_seq_num = next_seq_num + 1
                
                # start timer if not active and if there are unACK'd packets
                if not timer and window_idx < next_seq_num:
                    timer_start_time = time.time()
                    timer = True
                
                try:
                    data, server_address = send_socket.recvfrom(1024)
                    packet = Packet.bytes_to_packet(data)

                    if packet.packet_type == 1 and server_address[1] == dest_port and packet.seq_num >= window_idx:
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
                            packet = Packet(send_port, dest_port, seq, 0, message[seq])
                            send_socket.sendto(packet.packet_to_bytes(), (self.ip, dest_port))
                            print(f"resent packet {seq}")

                        timer_start_time = time.time()


            # send_socket.sendto(sentence.encode(), (self.ip, dest_port))

            # modified_sentence, server_address = client_socket.recvfrom(1024)
            # print(f"from server: ", modified_sentence.decode())
    

            # don't close socket or else it'll close socket if multiple ports are specified
            # send_socket.close()

        except KeyboardInterrupt:
            print(f"Forced stopping sending to port {dest_port}")
            exit()
        # except socket.error:
            # print(f"{self.ip} not responding on port {self.their_port}")
            # exit()
    

