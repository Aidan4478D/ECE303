import sys
import socket
import time
import string
from PortScanner import PortScanner, print_help

# target = input('What you want to scan?: ')
# port = int(input("Enter the port number to be scanned: "))

ports = None
ip = None
inp = None
outp = None

if len(sys.argv) > 1:
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--ports":
            r = sys.argv[i + 1].strip("[]")
            start_port, end_port = map(int, r.split('-'))
            
            ports = list(range(start_port, end_port + 1))
            # print(ports)
        if sys.argv[i] == "--ip":
            try:
                ip = sys.argv[i + 1]
            except:
                print("Bad input for IP")

        if sys.argv[i] == "--input":
            try:
                inp = sys.argv[i + 1]
            except:
                print("Bad input for input")

        if sys.argv[i] == "--output":
            try:
                outp = sys.argv[i + 1]
            except:
                print("Bad input for output")

        if sys.argv[i] == "--help":
            print_help()


start = time.time()
ps = PortScanner(ports, ip, inp, outp)
print(ps.scan_ports())

end = time.time()
print(f'Time taken {end-start:.2f} seconds')

