import sys
import threading
import time
import signal 

from Node import Node, timestamp 

ip = "localhost" 

def process_input(argv):
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <my_port> [receive <neighbor_listen_port> <loss_rate_p>...] [send <neighbor_listen_port>...] [last]")
        sys.exit(1)

    my_port = int(argv[1])
    send_to_ports = []  
    recv_from_ports_with_p = [] 

    last_seen = False
    
    i = 2
    current_mode = None 
    while i < len(argv):
        token = argv[i]
        if token == "receive":
            current_mode = "receive"
            i += 1
            continue
        elif token == "send":
            current_mode = "send"
            i += 1
            continue
        elif token == "last":
            last_seen = True
            i += 1
            # 'last' can be followed by other arguments if send/receive appear after it but typically it's the final argument.
            continue

        if current_mode == "receive":
            if i + 1 < len(argv) and argv[i].isdigit():
                loss_rate_val = float(argv[i+1])
                port = int(argv[i])
                recv_from_ports_with_p.append((port, loss_rate_val))
                i += 2
            else:
                print(f"incomplete 'receive' arguments near '{argv[i]}'. Expected <port> <loss_rate_p>.")
                i += 1
            
        elif current_mode == "send":
            if argv[i].isdigit():
                send_to_ports.append(int(argv[i]))
                i += 1
            else:
                print(f"unrecognized token '{argv[i]}' in 'send' mode, skipping.")
                i += 1
        elif token.isdigit() and current_mode is None:
             print(f"numeric token '{argv[i]}' found without 'receive' or 'send' mode. Please check syntax.")
             i += 1
        else:
            print(f"unrecognized token '{argv[i]}', skipping.")
            i += 1
            
    return my_port, send_to_ports, recv_from_ports_with_p, last_seen


my_port, gbn_send_to_ports, gbn_recv_from_ports_p, last_seen = process_input(sys.argv)

print(f"[{timestamp()}] Node {my_port} starting...")
print(f"    my listening port: {my_port}")
print(f"    will send GBN probes to: {gbn_send_to_ports}")
print(f"    will receive GBN probes from (port, p_drop): {gbn_recv_from_ports_p}")
# print(f"    is last node: {last_seen}")

node_instance = Node(ip, my_port, gbn_send_to_ports, gbn_recv_from_ports_p)
active_threads = []

receiver_thread = threading.Thread(target=node_instance.run_receiver, daemon=True, name=f"MasterRecv-{my_port}")
receiver_thread.start()
active_threads.append(receiver_thread)

dv_updater_thread = threading.Thread(target=node_instance.routine_dv_updater, daemon=True, name=f"DVUpdate-{my_port}")
dv_updater_thread.start()
active_threads.append(dv_updater_thread)

for target_port in gbn_send_to_ports:
    gbn_sender_thread = threading.Thread(target=node_instance.run_gbn_sender, args=(target_port,), daemon=True, name=f"GBNSend-{my_port}-to-{target_port}")
    gbn_sender_thread.start()
    active_threads.append(gbn_sender_thread)

if not last_seen:
    print(f"[{timestamp()}] Node {my_port}: Waiting for GBN START signal")
    # Main thread waits for start_event, GBN senders also wait internally now
    node_instance.start_event.wait() 
    print(f"[{timestamp()}] Node {my_port}: GBN START signal processed by main thread.")
else:
    print(f"[{timestamp()}] Node {my_port}: This is the last node, initiating GBN START broadcast after a delay...")
    time.sleep(2) 
    node_instance.broadcast_start_gbn()
    node_instance.start_event.set() # Set event for this node's own GBN senders
    print(f"[{timestamp()}] Node {my_port}: GBN START broadcast sent and local event set")
    print(f"[{timestamp()}] Node {my_port}: last node sending initial DV updates")
    node_instance.send_dv_updates_to_neighbors()

# some OS type shit to shut down program and close the ports properly
_node_instance_for_signal = node_instance
def signal_handler(sig, frame):
    print(f'\n[{timestamp()}] Node {_node_instance_for_signal.my_port}: Ctrl+C detected! Shutting down node...')
    _node_instance_for_signal.shutdown()
    print(f"[{timestamp()}] Node {_node_instance_for_signal.my_port}: Exiting main program.")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

try:
    while node_instance.running:
        all_threads_alive = any(t.is_alive() for t in active_threads)
        if not all_threads_alive and len(active_threads) > 0 :
             pass
        time.sleep(1) 
except KeyboardInterrupt: 
    signal_handler(None, None)
finally:
    if node_instance.running: 
        print(f"[{timestamp()}] Node {my_port}: Main loop exited unexpectedly. Forcing shutdown.")
        node_instance.shutdown()
    print(f"[{timestamp()}] Node {my_port}: Main thread finished.")
