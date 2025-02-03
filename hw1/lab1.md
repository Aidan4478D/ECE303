## Lab 1

Link to the lab: [https://academic.csuohio.edu/zhao-wenbing/wp-content/uploads/sites/67/2023/05/Wireshark_Intro_v8.0.pdf](https://academic.csuohio.edu/zhao-wenbing/wp-content/uploads/sites/67/2023/05/Wireshark_Intro_v8.0.pdf)

**Question 1** - Which of the following protocols are shown as appearing (i.e., are listed in the Wireshark “protocol” column) in your trace file: TCP, QUIC, HTTP, DNS, UDP, TLSv1.2?

 	DNS, HTTP, ICMP, QUIC (a lot), TCP, TLSv1.2, TLSv1.3, UDP

**Question 2** - How long did it take from when the HTTP GET message was sent until the HTTP OK reply was received? (By default, the value of the Time column in the packet listing window is the amount of time, in seconds, since Wireshark tracing began. (If you want to display the Time field in time-of-day format, select the Wireshark View pull down menu, then select Time Display Format, then select Time-of-day.)

    It took ~40ms after the GET request for the OK reply.

**Question 3** - What is the Internet address of the gaia.cs.umass.edu (also known as www net.cs.umass.edu)? What is the Internet address of your computer or (if you are using the trace file) the computer that sent the HTTP GET message?

    Computer Address: 192.168.0.106
    Internet Address: 128.119.245.12

**Question 4** - Expand the information on the HTTP message in the Wireshark “Details of selected packet” window (see Figure 3 above) so you can see the fields in the HTTP GET request message. What type of Web browser issued the HTTP request? The answer is shown at the right end of the information following the “User-Agent:” field in the expanded HTTP message display. [This field value in the HTTP message is how a web server learns what type of browser you are using.]

    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0

**Question 5** - Expand the information on the Transmission Control Protocol for this packet in the Wireshark “Details of selected packet” window (see Figure 3 in the lab writeup) so you can see the fields in the TCP segment carrying the HTTP message. What is the destination port number (the number following “Dest Port:” for the TCP segment containing the HTTP request) to which this HTTP request is being sent?

    Destination Port: 80

**Question 6** - Print the two HTTP messages (GET and OK) referred to in question 2 above. To do so, select Print from the Wireshark File command menu, and select the “Selected Packet Only” and “Print as displayed” radial buttons, and then click OK. 

    In files
