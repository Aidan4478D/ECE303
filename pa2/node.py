import sys
import threading
from Process import Node

ip = "localhost"

def process_input(argv):

    if len(argv) < 2:
        print(f"Usage: {argv[0]} <my_port> [receive <ports>...] [send <ports>...]")
        sys.exit(1)

    my_port = int(argv[1])
    send_ports = []
    recv_ports = []

    i = 2
    # print(sys.argv)
    while i < len(argv):
        if argv[i] == "receive":
            i += 1
            while i < len(argv) and argv[i].isdigit():
                recv_ports.append((int(argv[i]), float(argv[i+1])))
                i += 2
        elif argv[i] == "send":
            i += 1
            while i < len(argv) and argv[i].isdigit():
                send_ports.append(int(argv[i]))
                i += 1
        else:
            print(f"Warning: unrecognized token '{argv[i]}', skipping")
            i += 1

    return my_port, send_ports, recv_ports

my_port, send_ports, recv_ports = process_input(sys.argv)

print(f"my port is: {my_port}")
print(f"send ports are: {send_ports}")
print(f"recv ports are: {recv_ports}")

# create a different thread for each of the recievers
node = Node(ip, my_port, send_ports, recv_ports)

for port, p in recv_ports:
    t = threading.Thread(target=node.run_receiver, args=(port, p), daemon=True, name=f"recv-{my_port}-{port}")
    t.start()
    print(f"[{my_port}] Started recv-thread on port {port} (p={p})")

for port in send_ports:
    print(f"[{my_port}] Starting sender to port {port}")
    node.run_sender(port)
