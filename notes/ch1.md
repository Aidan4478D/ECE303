# Chapter 1 - Overview

- [What is the internet?](#what-is-the-internet)
- [What is a Protocol](#what-is-a-protocol)
- [Network edge: Hosts, Access Network, Physical Media](#network-edge-hosts-access-network-physical-media)
- [Network core: Packet Switching, Circuit Switching and Internet Structure](#network-core-packet-switching-circuit-switching-and-internet-structure)
- [Performance: Loss, Delay, and Throughput](#performance-loss-delay-and-throughput)
- [Network Security](#network-security)
- [Protocal Layers and Service Models](#protocal-layers-and-service-models)

## Questions
- Packet vs circuit switching clarification
- Do we have to know things like frequency division multiplexing or time division multiplexing
- Internet exchange points and peering links difference (slide 42)
- Go over the 4 types of delays and which arrows they represent
- Remember in the traceroute program: Why did some of the packets take less time being further along the road than others

## What is the internet?
### Internet as a "Nuts and Bolts" view
- Billions of connected computing devices
    - hosts = end systems
    - running network apps at internet's edge

- Packet switches: forward packets (chunks of data)
    - routers, switches

- Communication links
    - fiber, cooper, radio, satellite
    - transmission rate: bandwidth

- Networks: collection of devices, routers, links that are managed by an organization

- The internet is a "network of networks"
    - Interconnected by ISPS
    - Using protocols to contol sending and recieiving of messages (HTTP for web, TCP, IP, WiFi, etc.)
- Internet standards
    - RFC: Request for Comments
    - IETF: Internet Engineering Task Force

### Internet as a "Services View"
- Internet is an infrastructure that provides services to applications
    - Web, streaming video, multimedia teleconferencing, email, games, etc.
    - Provides programming interface to applications
        - Hooks allow sending/recieiving apps to "connect" tp use the internet transport service
        - Provides service options analogous to postal service

## What is a Protocol
- Protocols define the format & order of messages sent and recieved among network entities and actions taken on message transmission or recpetion

- Human protocols:
    - "What's the time?"
    - "I have a question"
    - Introductions

- Network protocols:
    - Computers rather than humans
    - All communication activity in internet governed by protocols

## Network edge: Hosts, Access Network, Physical Media
- Network edges:
    - Hosts: clients and servers
    - Servers are often in data centers
- Access networks, physical media
    - Wired, wireless communication links
- Network core:
    - Interconnected routers
    - Network of networks

- Connect end systems to edge routers using:
    - Residential access networks, institutional access networks, or mobile access networks (WiFi or 5G)

- Frequency division multiplexing (FDM) = different channels transmitted in different frequency bands
    - Used in cable-based access
    - Homes share access network to a cable headend (cable modem termination system that interacts with the ISP)
- There's also digital subscriber lines (DSL)
    - Use exisitng telephone line to the central office DSLAM (DSL access multiplexer)
    - Data over DSL phone line goes to internet
    - Voice over DSL phone line goes to telephone net
    - Thus voice and data are transmitted at different frequencies over dedicated line to the central office

- Wireless access networks
    - Shared wireless access network connects end system to router
    - Wireless local area networks (WLANs) typically within or around building
    - Wide-area cellular access networks provided by mobile, cellular network operator

- Enterprise networks
    - Companies, universities, etc.
    - Mix of wired, wireless link technologies, connecting a mix of switches and routers
        - Ethernet: wired access at high transmission rates
        - WiFi: wireless access points at lower transmission rates

- **Host**: sends packets of data
    - Takes an application message
    - Breaks it into smaller chunks known as *packets* of length L bits
    - Transmits packet into access network at transmission rate R
        - Link transmission rate aka link capacity aka link bandwidth
    - Packet transmission delay = time to transmit L-bit packet into link = L / R

- **Links**: Physical media
    - Bit: propagates between transmitter/reciever pairs
    - Physical Link: what lies between transmitter and reciever
    - Guided media: signals propagate in solid media (cooper, fiber, coax)
    - Unguided media: signals propagate freely (radio)

    - Twisted pair (TP): Two insulated cooper wires (category 5 and 6 both ethernet at different speeds 5 lower than 6)
    - Coaxial cable: two concentric bidirectional copper conductors
        - Multiple frequency channels on each cable with high speeds (100's Mbps) per channel
    - Fiber optic cable: Glass fiber carrying light pulses each pulse a bit
        - High speed point to point transmission (10's-100's Gbps)
        - Low error rate (repeaters spaced far apart and immune to EM noise)

    - Wireless radio:
        - Signals carried in various bands in the EM spectrum
        - No physical "wire"
        - Propagation environment effects (reflection, obstruction by objects, interference/noise)
    - Radio link types:
        - Wireless LAN (WiFi)
        - Wide-area (Cell tower)
        - Bluetooth (short ranges)
        - Terrestrial microwave (point to point)
        - Satellite (has a large end-to-end delay)

## Network core: Packet Switching, Circuit Switching and Internet Structure
- The network's core is a mesh of interconnected routers
- Packet-switching: hosts break application-layer messages into packets
    - Network forwards packets from one router to the next across links on path from source to destination

- Two key network-core functions
    - Forwarding (Switching)
        - Local action: move arriving packets from router's input link to appropriate router output link
        - Like the small scale decisions to go from A->B
    - Routing
        - Global action: determine source-destination paths taken by packets
        - Like the overall path/direction to go from A->B
        - Routing algorithms

- Packet Tansmission Delay: Takes L/R seconds to transmit (push) an L-bit packet into the link at R bps
- Store and Forward: The entire packet must arrive at the router before it can be transmitted on the next link
    - Queueing occurs when work arrives faster than it can be served
- Packet Queuing and Loss: If the arrival rate (in bps) to link > transmission rate (bps) of link for some period of time:
    - Packets will queue waiting to be transmitted on the output link
    - Packets can be dropped (lost) if memory (buffer) in router fills up


Circuit Switching
---
- End-to-end resources allocated to, reserved for "call" between source and destination
- Dedicated resources (no sharing)
- Has a circuit-like (guaranteed) performance
- Circuit segment idle if not used by call (no sharing)

- Frequency Division Multiplexing (FDM)
    - EM frequencies divided into narrow frequency bands
    - Each call allocated its own band can transmit at max rate of that narrow band

- Time Division Multiplexing (TDM)
    - Time divided into slots
    - Each call acllocated periodic slot(s) can transmit at max rate of (wider) frequency band (only) during its time slots

- Packet vs Circuit switching have different probability distributions (when determining how many users can use network under each type)
    - "packet switching" breaks data into smaller packets that can travel independently through a network, optimizing bandwidth usage and allowing for flexible routing
    - "circuit switching" establishes a dedicated, fixed communication path between two devices, guaranteeing consistent bandwidth but potentially wasting resources if not fully utilized
    - packet switching is more efficient for diverse data types
    - circuit switching prioritizes reliable, real-time communication like phone calls.

    - Packet switching is great for "bursty" data (sometimes there is data to send, other times there is not)
        - Resource sharing, simpler, no call setup
        - Excessive congestion is possible with packet delay and loss due to buffer overflow
        - Protocols needed for reliable data transfer and congestion control

Internet Structure
---
- Don't want to connect each access ISP to each other (O(N^2) connections!)
    - Thus have regional ISPs that access ISPs connect to
    - These regional ISPs are connected through internet exhange points (IXPs) or peering links
- There are also "Content provider networks" which are like companies that have their own services

- At the "center" there are a small number of well-connected large networks
    - "Tier-1" commerical ISPs (Sprint, AT&T, Frontier) which have national & international coverage
    - Content Provider networks (Google, Facebook) which are private networks that connects its data centers to the internet often bypassing tier-1 and regional ISPs


## Performance: Loss, Delay, and Throughput
- Packets queue into router buffers waiting for turn and transmission
    - Queue length grows when arrival rate to link (temporarily) exceeds output link capacity
- Packet loss occurs when memory to hold queued packets fills up

- Packet delay: four sources
    - d(nodal) = d(proc) + d(queue) + d(trans) + d(prop)
    - d(nodal) = nodal processing
        - Check bit errors
        - Determine output link
        - Ususally very very small (insignificant time)
    - d(queue) = queueing delay
        - Time waiting at output link for transmission
        - Depends on congestion level of router
    - d(trans) = transmission delay
        - L: Packet length (bits)
        - R: Link transmission rate (bps)
        - d(trans) = L/R
    - d(prop) = propagation delay
        - d: length of physical link
        - s: propagation speed (~2e8 m/s)
        - d(prop) = d/s

Note: d(trans) and d(prop) are very different!
- Transmission delay is the time it takes to send all bits of a packet onto a link
- Propagation delay is the time it takes for a signal to travel through a medium from sender to receive

- Packet queuing delay revisited
    - a: average packet arrival rate
    - L: packet length (bits)
    - R: link bandwidth (bit transmission rate)
    - Then **traffic intensity** = L * a / R
        - Arrival rate of bits / service rate of bits
    - La/R ~ 0: average queueing delay is small
    - La/R -> 1: average queueing delay is large
    - La/R > 1: "Work" arriviing is more than can be serviced

- Traceroute program: provides delay mesaurement from source -> router along end-end internet path towards destination
    - Sends three packets that will reach router *i* on path towards destination
    - Router *i* will return packets to sender
    - Sender measures time interval between transmission and reply

- Packet loss
    - Queue (buffer) preceding link in buffer has finite capacity
    - Packet arriving to full queue dropped (aka lost)
    - Lost packet may be retransmitted y previous node, by source end system, or not at all

- Throughput
    - Rate (bits/(time unit)) at which bits are being sent from sender to receiver
        - Instantaneous: rate at given point in time
        - Average: rate over longer period of time
    - Bottleneck link: link on end-end path that constrains end-end throughput
        - Like the limiting link

## Network Security
- Internet is not originally designed with much security in mind
- Packet sniffing = network interfaces that reads/records all packets passing by (including passwords!)
- IP spoofing = injection of packet with false source address
- Denial of Service = attackers make resources unavailable to legitimate traffic by overwhelming resource with bogus traffic

- Lines of defense:
    - Authentication: proving you are who you say you are (SIM card with cell networks)
    - Confidentiality: via encryption
    - Integrity checks: digital signatures prevent/detect tampering
    - Access restrictions: password-protected VPNs
    - Firewalls: specialized "middleboxes" in access and core networks  
        - off-by-default: filter incoming packets to restrict senders, receivers, applications
        - detecting/reacting to DOS attacks

## Protocal Layers and Service Models
- Application: Supporting network applications (HTTP, IMAP, SMTP, DNS)
- Transport: Process-Process data transfer (TCP, UDP)
- Network: Routing of datagrams from source to destination (IP, routing protocols)
- Link: data transfer between neighboring network elements (Ethernet, WiFi)
- Physical: bits "on the wire"

