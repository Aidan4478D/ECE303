import socket

class PortScanner():
    def __init__(self, ports, ip, outp):
        self.ports = (ports if ports is not None else list(range(1, 1024))) 
        self.ip = (ip if ip is not None else "localhost")
        self.output = outp

    def scan_ports(self):
        open_ports = []
        for p in self.ports:
            try:
                print(f"scanning port {p}")
                # AF_INET = internet address family for IPv4
                # SOCK_STREAM = socket type for TCP
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.25)

                result = s.connect_ex((self.ip, p))
                if result == 0:
                    try:
                        # Get the standard service name for the port
                        service = socket.getservbyport(p, 'tcp')
                        open_ports.append((p, service))
                    except OSError:
                        service = "Unknown"
                    print(f"Port {p} is open and is typically used for: {service}")
                s.close()           

            except KeyboardInterrupt:
                print(f"Forced scanning to stop on port {p}")
                exit()
            except socket.gaierror:
                print(f"Hostname could not be resolved on port {p}")
                exit()
            except socket.error:
                print(f"{self.ip} not responding on port {p}")
                continue
        
        return open_ports


    def output_results(self, results, mode):

        address = socket.gethostbyname(self.ip)
        message = f"Host: {address} ({self.ip})\n"
        message += f"Ports scanned: {self.ports}\n"
        message += f"------------------OPEN PORTS-----------------\n"
    
        if len(results) > 0:
            for r in results:
                message += f"Port: {r[0]}\tService: {r[1]}\n"
        else: 
            message += f"There were no open ports for range scanned.\n"
        


        if not self.output:
            init_message = "\nPort scanning complete!\n"
            init_message += message
            print(init_message)
        else:
            f = open(self.output, mode)
            f.write(message + "\n")
            f.close()
            print(f"Sent to the output to the file: {self.output}")


def print_help():
    message = """
    Welcome to the Port Scanner!

    Please run the scanner using `python3 scanner.py [option1, ..., option N]`

    The following options are:
        --ports <list of ports to scan of the form [start# - end#]>     ([1-1024] by default)
        --ip <IP address to scan>                                       (localhost by defualt)
        --input <file name>
        --output <file name>                                            (console by default)
    """

    print(message)


def input_from_file(inp, outp):
    f = open(inp, 'r')
    append = False
    for l in f:
        ip, start_port, end_port = l.strip().split()
        ports = list(range(int(start_port), int(end_port) + 1))
        ps = PortScanner(ports=ports, ip=ip, outp=outp)

        results = ps.scan_ports()
        
        # create a new file or append to one
        if append:
            ps.output_results(results, 'a')
        else:
            ps.output_results(results, 'w')
            append = True
