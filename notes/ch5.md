# Chapter 5 - Network Layer (Control Plane)

- [Routing Protocols](#routing-protocols)
- [Intra-ISP Routing OSPF](#ospf)
- [Routing Among ISPs: BGP](#bgp)
- [SDN Control Plane](#sdn-control-plane)
- [ICMP - Internet Control Message Protocol](#icmp)

## Questions
- Can we go over how dijkstra can cause oscillations
- What does it mean saying like advertises it "directly over IP rather than TCP/UDP" (slide 59)
- Just get a quick like control vs data plane explanation
- Do we have to know about SNMP stuff

## Network Layer - Control Plane
- Data plane: Forwarding = move packets from router's input to appropriate router's output
- Control plane: Routing = determine route taken by packets from source -> destination

Two approaches to structuring network control plane:
- Per router control (traditional) = routing algorithm components in each and every router
- Loclically centralized control (SDN) = remote controller computes & installs forwarding tables in routers

## Routing Protocols
- Determine "good" paths from sending -> receiving hosts thorugh network of routers
- Path = sequence of routers packets traverse from given initial source host to final destination host
- "Good" = least "cost", "fastest", "least congested"

- Global: all routers have **complete** topology and link cost info ==> "link state" algorithms
- Decentralized: iterative process of computation, exchange of info with neighbors
    - Routers initially only know link costs to attached neighbors
    - "Distance vector" algorithms

- Static: routes change slwoly over time
- Dynamic: Routes change more quickly

Link state (Dijkstra)
---
- Centralized: network topology, link costs known to all nodes
    - Accomplished via "link state broadcast"
    - All nodes have same info
- Computes least cost paths from one node ("source") to all other nodes
    - Gives forwarding table for that node
- Iterative: after k iterations, knows least cost path to k destinations

- Algorithm complexity of n nodes = O(N^2)
    - Each of n iteration: need to check all nodes, w, not in N
- Message complexity =k O(N^2)
    - Each router must broadcast its link state info to other n routers

- Route oscillations are possible

Distance Vector Algorithm
---
- Based on Bellman-Ford equation
- Weight is minimum of other connections to end plus costs

- Key idea:
    - From time-time each node sends its own distance vector estimate to neighbors
    - When x receives new DV estimate from any neighbor it updates its own DV using B-F equation
    - Under minor, natural conditions, the estimate converges to the actual least cost

- Each node:
    - Wait for change in local link cost or msg from neighbor
    - Recompute DV estimates using DV received from neighbors
    - If DV to any destination has changed, notify neighbors

- Each local iteration caused by:
    - Local link cost change
    - DV update message from neighbors
- Each node notifies neighbors only when its DV changes
    - Neighbors then notify their neighbors - only if neighbors
    - No notification received, no actions taken!

- "good news travels fast"
- "bad news travels slow"
    - can like oscillate to infinity if values aren't updated promptly

Comparison
---
Message complexity:
- Dijkstra: n routers, O(N^2) messages sent
- Dist Vec: Exchange between neighbors, convergence time varies

Speed of convergence:
- Dijkstra: O(N^2) algorithm, O(N^2) messages, may have oscillations
- Dist Vec: May have routing loops, count to infinity problem

Robustness (if malfunctions or is compromised)
- Dijkstra: router can advertise incorrect link cost, each router computes only its own table
- Dist Vec: router can advertise incorrect path cost (black holing), each router's DV used by others so error propagates

## OSPF
- Intra-ISP routing
- Study so far has been idealized
    - Can't store all billions of destinations in routing tables
    - Routing table exchange would swamp links
    - Each network admin may want to control routing in its own network

- Aggregate routers into regions known as "autonomous systems" (AS)
- Intra-AS (domain) routing among routers within same AS
    - All routers in AS must run same intra-domain protocol
    - Routers in different AS can run different intra-domain routing protocols
    - Gateway router: at "edge" of its own AS has link(s) to router(s) in other AS's

- Inter-AS routing among AS's
    - Gateways perform inter-domain routing (as well as intra-domain routing)

Most common intra-AS routing protocols:
- RIP = routing information protocol
    - Classic distance vector where DVs exchanged every 30s
    - No longer widely used
- EIGRP: Enhanced Interior Gateway Routing Protocol
    - DV based
    - Formerly Cisco-proprietary for decades
- OSPF: Open shortest path first
    - Link-state (dijkstra) routing
    - IS-IS protocl (essentially same as OSPF)

Open Shortest Path First routing
- openly available to everyone
- Classic link state (dijkstra)
    - Each router floods OSPF link-state advertisements (directly over IP rather than TCP/UDP) to all other routers in AS
    - Multiple link costs metrics possible: bandwitdh delay
    - Each router has full topology, sues Dijkstra's algortihm to compute forwarding table
- Security: all OSP messages authenticated (to prevent malicious intrusion)

Hiarchial OSPF
- Two-level hierarchy: local area, backbone
    - Link-state advertisements flooded only in area or backbone
    - each node has detailed area topology; only knows direction to reach other destinations
- Boundary router: connects to other AS's
- Backbone router: runs OSPF limited to backbone
- Area border routers: "summarize" distances to destinations in own area, advertise in backbone
- Local routers:
    - Flood LS in area only
    - compute routing within area
    - Forward packets to outside via area border router


## BGP
- Border Gateway Protocol
- The "de facto" inter-domain routing protocol
    - "Glue that holds internet together"
- Allows subnet to advertise its existence and the destinations it can reach to the rest of the internet
- Provides each AS as a mean to:
    - Obtain destination network reachability info from neighboring AS's (eBGP)
    - Determine routs to other networks based on reachability information and policy
    - Propagate reachability information to all AS-internal routers (iBGP)
    - Advertise destination reachability info to neighbors
- iBGP connections within AS
- eBGP connections between AS's
- Gateway routers run both eBGP and iBGP protocols

- BGP session: two BGP routers ("peers") exchange BGP messages over semi-permanent TCP connection
    - Advertising paths to different destination network prefixes ("path vector" protocol)
- BGP messages exchanged between peers over TCP connection
- BGP messages:
    - **OPEN**: opens TCP connection to remote BGP peer and authenticates sending BGP peer
    - **UPDATE**: advertises new path (or withdraws old)
    - **KEEPALIVE**: keeps connection alive in absence of UPDATES; also ACKs OPEN request
    - **NOTIFICATION**: reports errors in previous message, also used to close connection

- BFP advertised route: prefix + attributes
    - Prefix: destination being advertised
    - two important attributes:
        - AS-PATH: list of AS's through which prefix advertisement has passed
        - NEXT-HOP: indicates specific internal-AS router to next-hop AS
- Policy-based routing
    - Gateway receiving route advertisement uses uses import policy to accept/decline path
    - AS policy also determines whether to advertise path to other neighboring AS's
    - Based on policy, gateway router in AS can choose different paths and adviertise paths within its AS via iBGP
- Populates forwarding tables

- Hot potato routing = choose local gateway that has least intra-domain cost (don't worry about inter-domain cost)
    - Seems like greedy on intra scale
- Achieves policy via advertisements
    - ISP only wants to route traffic to/from its customer nodes (does not want to carry transit traffic between other ISPs)
    - Literally the homework questions

- BGP route selection = router may learn about more than one route destination to AS, selects route based on
    1. Local preference value attribute: policy decision
    2. Shortest AS-PATH
    3. Closest NEXT-HOP router: hot potato routing
    4. additional criteria

Inter vs. Intra
- Policy:
    - Inter-AS: admin wants control over how traffic routed, who routes through its network
    - Intra-AS: single admin, so policy less of an issue
- Scale:
    - Hierarchial routing saves table size, reduced update traffic
- Performance:
    - Intra-AS: can focus on performance
    - Inter-AS: policy dominates over performacne

## SDN Control Plane
- Software defined networking = remote controller computes, installs forwarding tables in routers
- Network layer historically implemented via distributed, per-router control approach
    - Individual routing algorithm in each and every router interact in control plane to compute forwarding tables

- Why a logically centralized control plane?
    - Easier network management: avoid router misconfig, greater flexibility of traffic flows
    - Table-based forwarding allows "programming" routers
        - Centralized "programming" easier: compute tables centrally and distribute
        - Distributed "programming" more difficult: compute tables as a result of distributed algorithm (protocol) implemented in each-and-every router
    - Open implementation of control plane

- Traffic engnineering is difficult with traditional routing (need to redefine link-weights so traffic routing algorithm computes routes accordingly)
- Forwarding and SDN can be used to achieve any routing desired

- Data plane switches:
    - Fast, simple, commodity switches implementing generalized data-plane forwarding in hardware
    - Flow (forwarding) table computed, installed under controller supervision
    - API for table-based switch control (defines what is and is not controllable)
    - Protocol for communicating with controller

- SDN controller (network OS)
    - Maintain network state information
    - Interacts with network control applications "above" via API
    - Interacts with network switches "below" via API
    - Implemented as distributed system for performance, scalability, fault-tolerance, robustness

- Network-control apps:
    - "Brains" of control: implement control functions using lower-level services, API provided by SDN controller

- Components of SDN controller
    - Interface layer to network control apps: abstractions API
    - Network0wide state management: state of network links, switches, services (a distributed database)
    - Communication: communicate between SDN controller and controlled switches

- OpenFlow protocol
    - Operates between controller & switch
    - TCP used to exchange messages
    - three classes:
        - Controller - switch
        - Asynchronous (switch - controller)
        - Symmetric (misc.)
    - Distinct from OpenFlow API (API used to specify generalized forwarding actions)

- Challenges
    - Hardening the control plane (dependable, reliable, performance-scalable, secure distributed system)
        - Robustness to failures: leverage strong theory of reliable distributed system for control plane
        - Dependability, security
    - Networks & protocols meeting mission-specific requirements
    - Internet-scaling: beyond a single AS
    - SDN critical in 5G cellular networks

## ICMP
- Used by hosts and routers to communicate network-level information
    - Error reporting: unreachable host, network, port, protocol
    - Echo request/reploy
- Network-layer "above" IP:
    - ICMP messages carried in IP datagrams
- ICMP messageL type, code plus first 8 bytes of IP datagram causing error

## SNMP
- Operator queries/sets devices data (MIB) using Simple Network Management Protocol (SNMP)
- 
