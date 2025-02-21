import socket

class PortScanner():
    def __init__(self, ports, ip, inp, outp):

        self.ports = (ports if ports is not None else [x for x in range(1, 1024)]) 
        self.ip = (ip if ip is not None else "localhost")
        self.input = inp
        self.output = outp

    def scan_ports(self):
        open_ports = []
        for p in self.ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)

                result = s.connect((self.ip, p))
                if not result:
                    open_ports.append(p)

                s.close()

            except socket.gaierror:
                print(f"Hostname could not be resolved on port {p}")
                exit()
            except socket.error:
                print(f"Server not responding on port {p}")
                continue


        return open_ports

    def open_input(self):
        
        return


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

