# Chapter 2 - Application Layer

- [Principles of Network Applications](#principles-of-network-applications)
- [Web and HTTP](#web-and-http)

## Questions
How do applications with P2P architectures have client and server processes (Ch2 slide 8)
Explain how persistent HTTP works

## Principles of Network Applications
- No need to write software for network-core devices (routers, switches, gateways, etc.)
    - They do not run on user-applications
    - Applications on end systems allows for rapid app development and propagation

**Client-server Paradigm**
- Clients:
    - Contact and communicate with the server
    - May be intermittently connected
    - May have dynamic IP addresses
    - Do not communicate directly with each other
    - Ex. HTTP, IMAP, FTP
- Server:
    - Always-on host
    - Permanent IP address
    - Often in data centers for scaling

**Peer-Peer Architecture**
- No always-on server
- Arbitrary end systems directly communicate
- Peers request servi e from other peers who provide service in return to other peers
    - New peers bring new servoce capacity as well as new service demands (self scaling)
- Peers are intermittently connected and change IP addresses
    - complex management

Pretty much everyone is connected to each other or everyone connects to a server

**Process Communicating**
- A process is a program running within a host
- Within the same host, two processes communicate using inter-process communication (as defined by OS)
- Processes in different hosts communicate by exchanging messages
- **Client process**: initiates communication
- **Server process**: waits to be contacted

Note: applications with P2P architectures have client and server processes

Sockets
---
- Process sends/recieves messages to/from its socket
- Socket analogous to door
    - Sending process shoves message out door
    - Sending process relies on transport infrastructure on other side of door to deliver message to socket at receiving process
    - Two sockets involved: one on each side

**Addressing Processes**
- Processes must have an identifier to receive messages
- Host has a unique 32-bit IP address
    - IP address of host on which process runs cannot be used for ID as many processes run on the same host
- The identifier includes both IP address and port numbers associated with process on host
    - Example port numbers are 80 (HTTP) and 25 (SMTP)

The application-layer protocol defines:
- Types of messages exchanged (request, response, etc.)
- Message syntax (how fields are structured and delineated)
- Message semantics (meaning of information in fielsd)
- Rules for when and how processes send and respond to messages
- Open protocols
    - Defined in RFCs (everyone has access to protocol definition)
    - Allows for easy exchange of info
- Proprietary protocols (skype, zoom, etc.)

Transport Service needed by App:
- Data integrity:
    - Some apps require 100% reliable data transfer (file transfer, web transactions, bank shit, etc.)
    - Other apps can tolerate some loss (audio, video, etc.)
- Timing:
    - Some apps require low delay to be "effective" (internet, telephony, interactive games, etc.)
- Throughput:
    - Some apps require minimum amount of throughbut to be "effective" (multimedia)
    - Other apps make use of whatever they got ("elastic apps")
- Security:
    - Encryption, data integrity, etc.

Internet Transport Protocol Services
---
**TCP Service**
- Reliable transport between sending and receiving process
- Flow control: sender won't overwhelm reciever
- Congestion control: throttle sender when network overloaded
- Connection-oriented: setup required between client and server processes
- Does not provide: timing, minimum throughput guarantee, security

**UDP Service**
- Unreliable data transfer between sending and receiving process
- Does not provide: reliability, flow control, congestion control, timing, throughput guarantee, security, or connection setup (wtf)
- UDP doesn't need to establish a connection or send acknowledgements, resulting in faster data transmission compared to TCP

Note: Use Transport Layer Security (TLS) to secure TCP
- Provides encrypted TCP connections, data integrity, and end-point authentication


## Web and HTTP
- Web page consists of objects, each of which can be stored on different Web servers
- Web page consists of base HTML-file which has several referenced objects, each addressable by a url
    - Ex. www.school.edu (host name) /some_dept/pic.gif (path name)

**HTTP Overview** (Hypertext transfer protocol)
- Web's application-layer protocol
- Client/server model
    - Client: browser that requests, recieves, and "displays" web objects
    - Server: Web server sends objects in response to requests
- HTTP uses TCP
    1. Client initiates TCP connection (creates socket) to server on port 80
    2. Server accepts TCP connection from client
    3. HTTP messages exchanged between browser (HTTP client) and web server (HTTP server)
    4. TCP connection closed
- HTTP is "stateless" as the server maintains no information about past client requests
    - Protocols that maintain "state" are complex as past state must be maintained and if it crashes the views may be inconsistent

Two Types of HTTP connections:
- Non-persistent HTTP
    1. TCP connection opened
    2. At most one object sent over TCP connection
    3. TCP connection closed
- Persistent HTTP
    1. TCP connection opened to a server
    2. Multiple objects an be sent over *single* TCP connection between client and that server
    3. TCP connection closed

**Round Time Trip (RTT)** = time for a small packet to travel from client to server and back
**HTTP Response Time** (per object)
- One RTT to initiate TCP connection
- One RTT for HTTP request and first few bytes of HTTP response to return
- Object/file transmission time

**HTTP Connection RTT**
- Non-persistent: 2RTT + File Transmission Time
    - Requires 2 RTTs per object
    - OS overhead for each TCP connection
    - Browsers often open multiple parallel TCP connections to fetch referenced objects in parallel
- Persistent:
    - Server leaves connection open after sending response
    - Subsequent HTTP messages between same client/server sent over open connection
    - Client sends requests as soon as it encounters a referenced object
    - As little as one RTT for all the referenced objects (cutting response time in half)

**HTTP Request** Messages:
- Includes request line (type, ex. `GET`, `POST`, `HEAD`) and header lines, then body
- In ASCII characters

- `POST` method
    - web page could sometimes include input
    - User input sent from client to server in body of `POST` request message
- `GET` method
    - Get data from server
- `HEAD` method
    - Requests headesr (only) that would be returned if specified URL were requested with an HTTP `GET` method
- `PUT` method
    - Uploads new file (object) to server
    - Completely replaces file that exists at specified URL with content in entity body of `POST` HTTP request message

Cookies
---
- HTTP `GET`/Resonse interaction is stateless
- There is no notion of multi-step exchanges of HTTP messages to ocmplete a web "transaction"
    - No need for client/server to track "state" of multi-step exchange
    - All HTTP requests are independent of each other
    - No need for client/server to "recover" from a partially completed by never completely completed transaction
- Sites and client browser use cookies to maintain some state between transactions
- Can be used for: authorization, shopping carts, recommendations, usr session state
    - Keep state at protocol endpoints (maintain state at sender/receiver over multiple transactions)
    - Also keep state in HTTP messages
- A "first-party" cookie allows site to remember preferences, login details, settings, etc.
    - Track user behavior on a given website
- A "third-party" cookie comes from site that you did not choose to visit
    - Track user behavior across multiple websites (without even visiting tracker site!)

**Four components to cookies**
1. Cookie header line of HTTP response message
2. Cookie header line in next HTTP request message
3. Cookie file kept on user's host managed by user's browser
4. Back-end database at web site

Web Caches
---
- Use to satisfy client requests without involving origin server 
- User configures browser to point to a (local) web cache
- Browser sends all HTTP requests to cache
    - If object in cache: return object to client
    - Else: cache requests object from origin server, caches received object, then returns object to client

- Acts as both a client and a server (client to origin server, server to original user)
- Server tells cache about object's allowable caching in response header (`Cache-Control` field in header)
- Use to reduce response time for client request (cache is closer to client)
- Reduces traffic on an institution's access link
- Use when internet is dense with caches (enables "poor" content providers to deliver content more effectively)

- Access link utilization is: avg. data rate to browsers / access link rate
    - Remember high utilization (close to 1) = large queueing delays
