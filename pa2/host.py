from Process import Node

ip = "localhost"
my_port = input("Enter your port: ")
their_port = input("Enter their port: ")


p = Node(ip, my_port, their_port)
p.run_receiver()
