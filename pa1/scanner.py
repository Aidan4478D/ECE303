import sys
import socket
import time
import string
from PortScanner import PortScanner, print_help, input_from_file

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
                exit()

        if sys.argv[i] == "--input":
            try:
                inp = sys.argv[i + 1]
            except:
                print("Bad input for input")
                exit()

        if sys.argv[i] == "--output":
            try:
                outp = sys.argv[i + 1]
            except:
                print("Bad input for output")
                exit()

        if sys.argv[i] == "--help":
            print_help()


start = time.time()

if inp is not None:
    input_from_file(inp, outp)

else:
    ps = PortScanner(ports, ip, outp)

    results = ps.scan_ports()
    ps.output_results(results, 'w')

end = time.time()
print(f'Time taken {end-start:.2f} seconds')

