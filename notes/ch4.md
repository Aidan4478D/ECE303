# Chapter 4 - Network Layer

- [Network Layer: Data Plane](#network-layer-data-plane)
- [What's inside a router](#whats-inside-a-router)
- [IP - Internet Protocol](#ip-internet-protocol)

## Questions
- Can we go over the pros/cons of the different aspects of a router (in class quiz)

## Network Layer - Data Plane
- Routers
    - Examines header fields in all IP datagrams passing through it
    - Moves datagrams from input ports to output ports to transfer datagrams along end-end path

- Basic functions:
    - Forwarding: move packets from a router's input link to appropriate router output link
        - Getting through single interchange
    - Routing: determine route taken by packets from source to destination
        - Planning from start to finish

- Data Plane:
    - Local, per-router function
    - Determines how datagram arriving on router input port is forwarded to router output port
- Control Plane
    - Network-wide logic
    - Determines how datagram is routed among routers along end-end path from source host to dest host
    - Two control-plane approaches
        - Traditional routing algorithms (implemented in routers)
        - Sofrware-defined networking (SDN) (implemented in remote servers)

- Service model:
    - "best effort" as in no guarantees on:
        - Successful datagram delivery to destination
        - Timing or order of delivery
        - Bandwidth available to end-end flow
    - Allowed internet to be widely deployed and adpoted
    - Allows performance of real-time applications
    - Allow services to be provided from multiple locations
    - Congestion control of "elastic" services helps

## What's Inside a Router
![Router Overview](images/ch4_router.png)

- Input ports
    - Physical layer: bit-level reception
    - Link layer: Ethernet/wireless
    - Decentralized switching
        - Use header field values, lookup output port using forwarding table in input port memory
        - Goal: complete input port processing at 'line speed'
        - Input port queuing: if datagrams arrive faster than forwarding rate into switch fabric
    - Forwarding options:
        - **Destination-based forwarding**: forward based only on destination IP address
        - **Generalized forwarding**: Forward based on any set of header field values

**Longest prefix matching**: when looking for forwarding table entry for given destination address, use longest address prefix that matches destination address

- Switching fabrics
    - Transfer packet from input link to appropriate output link
    - Switching rate: rate at which packets can transfer from inputs to outputs
        - Often measured as a multiple of input/output line rate
        - N inputs: switching rate N times line rate desireable
    - Three major types: memory, bus, interconnection network

    - Switching via memory:
        - Used under direct control of CPU
        - Packet copied into system memory
        - Speed limited by memory bandwidth (2 bus crossings per datagram)
    - Switching via bus:
        - Datagram from input port memory to ouput port memory via a shared bus
        - Bus contention: switching speed limited by bus bandwidth
    - Switching via interconnection network:
        - nxn switch from multiple stages of smaller switches
        - Initially developed to connect processors in multi-processors
        - Can be parallelized (can use multiple switching "planes" in parallel)

- Input port queuing
    - If switch fabric speed < input ports combined 
    - Head of line (HOL) blocking could exist like before!
- Output port queuing
    - Buffering arrival rate via switch exceeds output line speed
    - Queueing (delay) and loss due to output port buffer overflow
    - Buffering required when datagrams arrive from fabric faster than link transmission rate
        - Datagrams can be lost due to congestion, lack of buffers
    - Scheduling discipline chooses among queued datagrams for transmission
        - Priority scheduling: who gets best performance (net neutrality)

    - Average buffering equal to "typical" RTT
    - More recent: with N flows, buffering = RTT * C / sqrt(N)
    - Too much buffering can increase delays

- Buffer management: 
    - Drop: which packet to add, drop when buffers are full (tail = drop arriving, priority = drop based on priority basis)
    - Marking: which packets to mark to signal congestion
- Packet scheduling:
    - Deciding on which packet to send next on link (first come-first serve, priority, round robin, weighted fair queueing)
    - First come first serve: packets transmitted in order of arrival to output port
    - Priority scheduling:
        - Arriving traffic classified, queued by class (classify by header field)
        - Send packet from highest priority queue that has buffered packets (FCFS within priority class)
    - Round Robin scheduling:
        - Arriving traffic classified, queued by class (classify be header field)
        - Server cyclically, repeatedly scans class queues, sending one complete packet from each class (if available) in turn
    - Weighted fair queuing:
        - Generalized round robin
        - Each class, i, has a weight w(i) and gets weighted amount of service in each cycle w(i) / sum(w(j))
        - Minimum bandwidth guarantee

## IP - Internet Protocol

