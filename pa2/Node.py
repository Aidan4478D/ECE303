from socket import *
import time
import random
import threading
import struct
import json # For DV

from Packet import Packet
from datetime import datetime

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

class Node():
    def __init__(self, ip, my_port, send_ports, recv_ports_with_p, window_size=5):
        self.my_port = int(my_port)
        self.send_ports = send_ports # List of ports to send GBN probes to
        self.recv_ports_with_p = recv_ports_with_p # List of tuples (port, p_loss) to receive GBN probes from

        self.ip = (ip if ip is not None else "localhost")
        self.window_size = int(window_size)

        # sockets
        self.recv_socket = socket(AF_INET, SOCK_DGRAM) # For receiving GBN Probes, DV, GBN Start
        self.recv_socket.bind(('0.0.0.0', self.my_port))

        self.send_socket = socket(AF_INET, SOCK_DGRAM) # For sending GBN Probes and receiving their ACKs
        self.send_socket.bind(('0.0.0.0', 0))
        self.actual_send_port = int(self.send_socket.getsockname()[1])
        self.send_socket.settimeout(0.5)

        # DV Attributes
        self.peers = set(self.send_ports) | {port for (port, _) in self.recv_ports_with_p}
        self.dv_lock = threading.Lock()
        self.routing_table = {} # stores Dx(y) = (cost, next_hop_to_y)
        self.direct_link_costs = {} # stores c(self, peer) for direct peers
        self.initialize_routing_table() # initializes both tables

        self.start_event = threading.Event()
        self.running = True

        # GBN Loss tracking for DV
        self.link_loss_stats = {dest_port: {'sent': 0, 'lost_by_timeout': 0, 'loss_rate': 0.0, 'last_printed_sent':0, 'last_printed_lost':0} for dest_port in self.send_ports}
        self.gbn_interval_timer = {}

    def initialize_routing_table(self):
        with self.dv_lock:
            self.routing_table[self.my_port] = (0.0, self.my_port)
            self.direct_link_costs[self.my_port] = 0.0 # Cost to self is 0

            for peer_port in self.peers:
                if peer_port != self.my_port:
                    self.direct_link_costs[peer_port] = 0.0
                    # Initial routing table entry for peers is via this direct link
                    self.routing_table[peer_port] = (0.0, peer_port)
        print(f"[{timestamp()}] Node {self.my_port} Initialized Routing Table and Direct Link Costs:")
        self.print_routing_table()



    def print_routing_table(self):
        print(f"[{timestamp()}] Node {self.my_port} Routing Table")
        with self.dv_lock:
            if not self.routing_table:
                print("- (empty)")
                return
            sorted_dests = sorted(self.routing_table.keys())
            for dest in sorted_dests:
                cost, next_hop = self.routing_table[dest]
                cost_str = f"{cost:.2f}"
                if dest == self.my_port or next_hop == self.my_port :
                    print(f"- ({cost_str}) -> Node {dest}")
                elif next_hop == dest:
                    print(f"- ({cost_str}) -> Node {dest}")
                else:
                    print(f"- ({cost_str}) -> Node {dest} ; Next hop -> Node {next_hop}")
        print("-" * 30)


    # to start up network
    def broadcast_start_gbn(self):
        print(f"[{timestamp()}] Node {self.my_port} broadcasting GBN START to {sorted(list(self.peers))}")
        for peer_port in self.peers:
            if peer_port == self.my_port: continue
            packet = Packet(self.actual_send_port, peer_port, 0, 2)
            try:
                temp_sock = socket(AF_INET, SOCK_DGRAM)
                temp_sock.sendto(packet.packet_to_bytes(), (self.ip, peer_port))
                temp_sock.close()
            except Exception as e:
                print(f"[{timestamp()}] Node {self.my_port} ERROR broadcasting GBN START to {peer_port}: {e}")


    # send the D_x(y) values from the routing_table
    def send_dv_updates_to_neighbors(self):
        table_to_send_payload = ""
        with self.dv_lock:
            table_to_send_dict = {str(dest): round(cost, 2) for dest, (cost, _) in self.routing_table.items()}
            table_to_send_payload = json.dumps(table_to_send_dict)

        for neighbor_port in self.peers:
            if neighbor_port == self.my_port:
                continue
            dv_packet = Packet(self.my_port, neighbor_port, 0, 3, table_to_send_payload)
            try:
                temp_sock = socket(AF_INET, SOCK_DGRAM)
                temp_sock.sendto(dv_packet.packet_to_bytes(), (self.ip, neighbor_port))
                temp_sock.close()
                print(f"[{timestamp()}] Node {self.my_port}: Table sent to Node {neighbor_port}")
            except Exception as e:
                print(f"[{timestamp()}] Node {self.my_port}: Error sending DV update to {neighbor_port}: {e}")

        self.print_routing_table()



    def handle_dv_packet(self, dv_packet_obj, sender_udp_address):
        dv_sender_main_port = dv_packet_obj.source_port
        print(f"[{timestamp()}] Node {self.my_port}: Table received from Node {dv_sender_main_port}")

        try:
            received_table_str_keys = json.loads(dv_packet_obj.data.decode())
            # received_table contains D_v(y) for neighbor v=dv_sender_main_port
            received_table_Dv = {int(k): float(v) for k, v in received_table_str_keys.items()}
        except Exception as e:
            print(f"[{timestamp()}] Node {self.my_port}: Error processing DV data from {dv_sender_main_port}: {e}")
            return

        table_changed = False
        with self.dv_lock:
            if dv_sender_main_port not in self.peers:
                print(f"[{timestamp()}] Node {self.my_port}: Received DV from unknown peer {dv_sender_main_port}. Ignoring.")
                return

            # determine/update direct link cost c(self, dv_sender_main_port)
            # This is c(X,V) where X is self, V is dv_sender_main_port
            actual_c_X_V = float('inf')

            if dv_sender_main_port in self.send_ports:
                actual_c_X_V = self.direct_link_costs.get(dv_sender_main_port, float('inf'))
            else:
                is_gbn_receiver_from_dv_sender = any(p == dv_sender_main_port for p, _ in self.recv_ports_with_p)
                if is_gbn_receiver_from_dv_sender:
                    cost_dv_sender_to_self_DvX = received_table_Dv.get(self.my_port, float('inf'))
                    symmetric_cost_cX_V = round(cost_dv_sender_to_self_DvX, 2)

                    current_direct_cost_to_dv_sender = self.direct_link_costs.get(dv_sender_main_port, float('inf'))
                    if round(current_direct_cost_to_dv_sender, 2) != symmetric_cost_cX_V:
                        self.direct_link_costs[dv_sender_main_port] = symmetric_cost_cX_V
                        # print(f"[{timestamp()}] Node {self.my_port}: Direct link cost c({self.my_port},{dv_sender_main_port}) updated to {symmetric_cost_cX_V:.2f} by symmetry from D({dv_sender_main_port},{self.my_port}).")
                        table_changed = True
                    actual_c_X_V = symmetric_cost_cX_V
                else:
                    actual_c_X_V = self.direct_link_costs.get(dv_sender_main_port, float('inf'))

            if actual_c_X_V != float('inf'):
                current_cost_to_dv_sender_in_table, current_next_hop_to_dv_sender = self.routing_table.get(dv_sender_main_port, (float('inf'), None))
                if actual_c_X_V < round(current_cost_to_dv_sender_in_table, 2) or \
                   (current_next_hop_to_dv_sender == dv_sender_main_port and round(current_cost_to_dv_sender_in_table, 2) != actual_c_X_V):
                    self.routing_table[dv_sender_main_port] = (actual_c_X_V, dv_sender_main_port)
                    # print(f"[{timestamp()}] Node {self.my_port}: Path to peer {dv_sender_main_port} updated to direct cost {actual_c_X_V:.2f}.")
                    table_changed = True

            for dest_Y, cost_Dv_Y in received_table_Dv.items():
                if dest_Y == self.my_port:
                    continue

                if actual_c_X_V == float('inf'):
                    continue

                new_cost_to_Y_via_V = round(actual_c_X_V + cost_Dv_Y, 2)
                current_cost_to_Y_DxY, current_next_hop_to_Y = self.routing_table.get(dest_Y, (float('inf'), None))

                if new_cost_to_Y_via_V < round(current_cost_to_Y_DxY, 2):
                    self.routing_table[dest_Y] = (new_cost_to_Y_via_V, dv_sender_main_port)
                    table_changed = True

                # Path already via V, but cost changed
                elif current_next_hop_to_Y == dv_sender_main_port and round(current_cost_to_Y_DxY, 2) != new_cost_to_Y_via_V:
                    self.routing_table[dest_Y] = (new_cost_to_Y_via_V, dv_sender_main_port)
                    table_changed = True

        if table_changed:
            # print(f"[{timestamp()}] Node {self.my_port}: Routing table changed due to update from {dv_sender_main_port}.")
            self.send_dv_updates_to_neighbors()
        # else:
            # print(f"[{timestamp()}] Node {self.my_port}: Routing table NOT changed by update from {dv_sender_main_port}. Current table:")
            # self.print_routing_table()


    def routine_dv_updater(self):
        last_sent_rounded_table_snapshot = {}
        initial_send_done = False

        while self.running:
            time.sleep(5)
            if not self.start_event.is_set():
                continue

            current_rounded_table_snapshot = {}
            perform_routine_send = False
            with self.dv_lock:
                for dest, (cost, _) in self.routing_table.items():
                    current_rounded_table_snapshot[dest] = round(cost, 2)

                if not initial_send_done:
                    perform_routine_send = True
                    initial_send_done = True
                    # print(f"[{timestamp()}] Node {self.my_port}: Preparing initial/periodic DV update.")
                elif current_rounded_table_snapshot != last_sent_rounded_table_snapshot:
                    perform_routine_send = True
                    # print(f"[{timestamp()}] Node {self.my_port}: Routine DV update triggered by cost changes.")

                if perform_routine_send:
                    last_sent_rounded_table_snapshot = current_rounded_table_snapshot.copy()

            if perform_routine_send:
                self.send_dv_updates_to_neighbors()


    def run_receiver(self):
        # print(f"[{timestamp()}] Node {self.my_port}: receiver started on port {self.my_port}.")
        expected_gbn_probe_seq_nums = {port: 0 for (port, _) in self.recv_ports_with_p}
        gbn_probe_drop_p = {port: p for (port,p) in self.recv_ports_with_p}

        while self.running:
            try:
                data_bytes, client_address = self.recv_socket.recvfrom(2048)
                if not data_bytes: continue

                packet = Packet.bytes_to_packet(data_bytes)

                if packet.dest_port != self.my_port and packet.packet_type not in [2, 3]: # GBN Start, DV
                    continue
                if packet.packet_type == 3 and packet.dest_port != self.my_port : # DV packets must be addressed to my_port
                    continue

                if packet.packet_type == 2: # GBN START
                    if not self.start_event.is_set():
                        # print(f"[{timestamp()}] Node {self.my_port} got GBN START from {packet.source_port}")
                        self.broadcast_start_gbn()
                        self.start_event.set()
                elif packet.packet_type == 3: # DV Update
                    if self.start_event.is_set():
                        self.handle_dv_packet(packet, client_address)
                elif packet.packet_type == 0: # GBN Probe
                    if not self.start_event.is_set():
                        continue

                    gbn_sender_main_port = packet.source_port
                    p_drop = gbn_probe_drop_p.get(gbn_sender_main_port, 0)
                    current_expected_seq = expected_gbn_probe_seq_nums.get(gbn_sender_main_port, 0)

                    if random.random() < p_drop:
                        # print(f"[{timestamp()}] Node {self.my_port} [recv GBN probe from Node {gbn_sender_main_port}] dropped seq={packet.seq_num} (data='{packet.data.decode()}')")
                        continue

                    if packet.seq_num == current_expected_seq:
                        # print(f"[{timestamp()}] Node {self.my_port} [recv GBN probe from Node {gbn_sender_main_port}] {packet.data.decode()} (seq num: {packet.seq_num})")
                        ack_packet = Packet(self.my_port, gbn_sender_main_port, packet.seq_num, 1)
                        self.recv_socket.sendto(ack_packet.packet_to_bytes(), client_address)
                        expected_gbn_probe_seq_nums[gbn_sender_main_port] = current_expected_seq + 1
                    else:
                        if current_expected_seq > 0: # Only send ACK for previous if we've ACKed at least one
                            #print(f"[{timestamp()}] Node {self.my_port} [recv GBN probe from Node {gbn_sender_main_port}] Out of order: got {packet.seq_num}, expected {current_expected_seq}. Re-ACKing {current_expected_seq - 1}")
                            ack_packet = Packet(self.my_port, gbn_sender_main_port, current_expected_seq - 1, 1)
                            self.recv_socket.sendto(ack_packet.packet_to_bytes(), client_address)
            except timeout:
                continue
            except ConnectionResetError:
                print(f"[{timestamp()}] Node {self.my_port} Master receiver: ConnectionResetError.")
                time.sleep(0.1)
            except Exception as e:
                print(f"[{timestamp()}] Node {self.my_port} Master receiver exception: {e} with data '{data_bytes if 'data_bytes' in locals() else 'N/A'}' from {client_address if 'client_address' in locals() else 'N/A'}")
                time.sleep(0.1)

        print(f"[{timestamp()}] Node {self.my_port} Master receiver shutting down.")

    # function is called by a GBN sender thread for the link: self.my_port -> dest_gbn_target_port
    def update_link_cost_for_dv(self, dest_gbn_target_port, calculated_loss_rate):
        table_needs_update_check = False
        new_rounded_cost = round(calculated_loss_rate, 2)

        with self.dv_lock:
            current_direct_cost = self.direct_link_costs.get(dest_gbn_target_port, float('inf'))

            if round(current_direct_cost, 2) != new_rounded_cost:
                self.direct_link_costs[dest_gbn_target_port] = calculated_loss_rate
                # print(f"[{timestamp()}] Node {self.my_port}: Direct link cost c({self.my_port},{dest_gbn_target_port}) updated by GBN to {calculated_loss_rate:.4f} (rounded: {new_rounded_cost:.2f}).")
                table_needs_update_check = True

            # Also update the routing_table if this direct path is the best/current path to dest_gbn_target_port
            if table_needs_update_check: # or always check if the direct path cost should update the table
                current_routing_cost, current_next_hop = self.routing_table.get(dest_gbn_target_port, (float('inf'), None))

                # if the path in table is currently direct, or if this new direct cost is better
                if current_next_hop == dest_gbn_target_port: # Path is already direct
                    if round(current_routing_cost, 2) != new_rounded_cost:
                        self.routing_table[dest_gbn_target_port] = (calculated_loss_rate, dest_gbn_target_port)
                        print(f"[{timestamp()}] Node {self.my_port}: Routing table entry for direct peer {dest_gbn_target_port} updated to GBN cost {new_rounded_cost:.2f}.")

                # new direct path is better than current indirect
                elif new_rounded_cost < round(current_routing_cost, 2) : 
                     self.routing_table[dest_gbn_target_port] = (calculated_loss_rate, dest_gbn_target_port)
                     print(f"[{timestamp()}] Node {self.my_port}: Routing table entry for {dest_gbn_target_port} updated to new better direct GBN cost {new_rounded_cost:.2f}.")


    def run_gbn_sender(self, dest_port):
        print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Thread started.")

        if not self.start_event.is_set():
            print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Waiting for global start event...")
            self.start_event.wait()
            print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Global start event received, proceeding.")

        probe_data_stream = ['h', 'e', 'l', 'l', 'o']
        next_seq_num_gbn = 0
        window_base_gbn = 0

        sent_for_interval = 0
        timed_out_for_interval = 0 

        gbn_timer_active = False
        gbn_timer_start_time = 0
        gbn_timeout_duration = 0.5 # 500ms

        # initialize stats for this GBN link
        with self.dv_lock: 
            self.link_loss_stats[dest_port] = {'sent':0, 'lost_by_timeout':0, 'loss_rate':0.0, 'last_printed_sent':0, 'last_printed_lost':0}
        self.gbn_interval_timer[dest_port] = time.time()

        packets_sent_this_session = 0 # To eventually stop the sender thread

        while self.running:
            while next_seq_num_gbn < window_base_gbn + self.window_size and self.running:
                data_char_to_send = probe_data_stream[next_seq_num_gbn % len(probe_data_stream)]
                packet = Packet(self.my_port, dest_port, next_seq_num_gbn, 0, data_char_to_send) # Type 0 for GBN probe
                self.send_socket.sendto(packet.packet_to_bytes(), (self.ip, dest_port))
                sent_for_interval += 1
                packets_sent_this_session +=1

                if not gbn_timer_active:
                    gbn_timer_start_time = time.time()
                    gbn_timer_active = True

                next_seq_num_gbn += 1
                # time.sleep(0.02) # Small delay between sends so it isn't too overwhelming

            # receive ACK
            try:
                if not self.running: break
                ack_data_bytes, server_address = self.send_socket.recvfrom(1024)
                ack_packet = Packet.bytes_to_packet(ack_data_bytes)

                if ack_packet.packet_type == 1 and ack_packet.source_port == dest_port and ack_packet.dest_port == self.my_port :
                    if ack_packet.seq_num >= window_base_gbn: # Cumulative ACK
                        window_base_gbn = ack_packet.seq_num + 1
                        # all outstanding packets ACKd
                        if window_base_gbn == next_seq_num_gbn:
                            gbn_timer_active = False
                        # restart timer still outstanding packets
                        else: 
                            gbn_timer_start_time = time.time()
            except timeout:
                if gbn_timer_active and (time.time() - gbn_timer_start_time >= gbn_timeout_duration):
                    # print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: TIMEOUT for window base {window_base_gbn}. Resending window.")
                    
                    # resent packets are not double-counted in sent_for_interval here, sent_for_interval counts original transmissions in the window.
                    # loss is based on timeouts leading to retransmissions.

                    num_lost_this_timeout = next_seq_num_gbn - window_base_gbn
                    timed_out_for_interval += num_lost_this_timeout

                    temp_seq = window_base_gbn
                    while temp_seq < next_seq_num_gbn:
                        data_char_to_send = probe_data_stream[temp_seq % len(probe_data_stream)]
                        packet = Packet(self.my_port, dest_port, temp_seq, 0, data_char_to_send)
                        self.send_socket.sendto(packet.packet_to_bytes(), (self.ip, dest_port))
                        temp_seq += 1

                    # restart timer
                    gbn_timer_start_time = time.time()
            except Exception as e:
                if self.running:
                    print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Exception in GBN sender ACK recv: {e}")
                break

            # update DV stuff
            current_time = time.time()
            if current_time - self.gbn_interval_timer.get(dest_port, 0) >= 5.0:
                # only calculate if packets were sent in this interval
                if sent_for_interval > 0: 
                    with self.dv_lock: # protect link_loss_stats
                        self.link_loss_stats[dest_port]['sent'] += sent_for_interval
                        self.link_loss_stats[dest_port]['lost_by_timeout'] += timed_out_for_interval

                        cumulative_sent = self.link_loss_stats[dest_port]['sent']
                        cumulative_lost = self.link_loss_stats[dest_port]['lost_by_timeout']

                        current_overall_loss_rate = (cumulative_lost / cumulative_sent) if cumulative_sent > 0 else 0.0
                        self.link_loss_stats[dest_port]['loss_rate'] = current_overall_loss_rate

                    # interval-specific print
                    interval_loss_rate_for_print = (timed_out_for_interval / (sent_for_interval + timed_out_for_interval)) if sent_for_interval > 0 else 0.0
                    print(f"[{current_time:.3f}] Node {self.my_port} --> Node {dest_port}: {timed_out_for_interval}/{sent_for_interval + timed_out_for_interval} probes lost, loss rate {interval_loss_rate_for_print:.2f}")

                    # update DV link cost with the cum loss rate
                    self.update_link_cost_for_dv(dest_port, current_overall_loss_rate)

                sent_for_interval = 0
                timed_out_for_interval = 0 # reset for next 5 sec interval
                self.gbn_interval_timer[dest_port] = current_time

            # condition to stop sender threads after some time
            # aka send "hello" 20 times for each sender
            if packets_sent_this_session > 100: # Example: stop some nodes earlier for testing
                print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Transmitted \"hello\" 20 times ({packets_sent_this_session}).")
                break

        print(f"[{timestamp()}] Node {self.my_port} GBN_SEND -> {dest_port}: Thread stopping.")


    # attempt to close sockets nicely
    def shutdown(self):
        print(f"[{timestamp()}] Node {self.my_port} shutting down...")
        self.running = False
        self.start_event.set()

        try:
            unblock_sock = socket(AF_INET, SOCK_DGRAM)
            unblock_sock.sendto(b'unblock', (self.ip if self.ip != '0.0.0.0' else '127.0.0.1', self.my_port))
            unblock_sock.close()
        except Exception as e:
            print(f"[{timestamp()}] Node {self.my_port} error sending unblock packet: {e}")
        
        
        try:
            if self.recv_socket: self.recv_socket.close()
        except Exception as e: print(f"Error closing recv_socket: {e}")
        try:
            if self.send_socket: self.send_socket.close()
        except Exception as e: print(f"Error closing send_socket: {e}")

        print(f"[{timestamp()}] Node {self.my_port} shutdown sequence complete.")
