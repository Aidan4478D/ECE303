import socket

class PortScanner():
    def __init__(self, ports, ip, outp):

        self.ports = (ports if ports is not None else [x for x in range(1, 1024)]) 
        self.ip = (ip if ip is not None else "localhost")
        self.output = outp

    def scan_ports(self):
        open_ports = []
        for p in self.ports:
            try:
                # AF_INET = internet address family for IPv4
                # SOCK_STREAM = socket type for TCP
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)

                result = s.connect((self.ip, p))
                if not result:
                    open_ports.append(p)
                    print(f"Port {p} is open!")

                s.close()

            except socket.gaierror:
                print(f"Hostname could not be resolved on port {p}")
                exit()
            except socket.error:
                print(f"{self.ip} not responding on port {p}")
                continue

        return open_ports


    def output_results(self, results, mode):
        if not self.output:
            print(f"For ip {self.ip}, the port(s) {results} are open")
        else:
            f = open(self.output, mode)
            f.write(f"For ip {self.ip}, the port(s) {results} are open\n")
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
