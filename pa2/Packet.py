import struct

class Packet():
    def __init__(self, source_port, dest_port, seq_num, packet_type, data=None):
        self.source_port = int(source_port)
        self.dest_port = int(dest_port)
        self.seq_num = int(seq_num) # Used by GBN, can be 0 or sequence for DV updates
        self.packet_type = packet_type  # 0 for GBN probe, 1 for GBN ACK, 2 for GBN start, 3 for DV Update

        if packet_type == 0: # GBN Probe
            if isinstance(data, str):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data.encode()
            elif isinstance(data, bytes):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data
            else:
                raise ValueError(f"invalid data type for probe packet: {type(data)}")
        elif packet_type == 1 or packet_type == 2:
            self.data = None
        elif packet_type == 3:
            if isinstance(data, str):
                self.data = data.encode() 
            elif isinstance(data, bytes):
                self.data = data
            else:
                raise ValueError(f"Invalid data type for DV packet: {type(data)}, expected str or bytes")
        else:
            raise ValueError(f"invalid packet type: {packet_type}")

    def packet_to_bytes(self):
        # >: big endian
        # h: short = 16 bits ==> 2 bytes
        # i: int = 32 bits ==> 4 bytes
        # b: char = 8 bits ==> 1 byte
        # caps = unsigned

        if self.packet_type == 0:
            data_val = self.data[0] if self.data else 0
            header = struct.pack(">BHHIB", self.packet_type, self.source_port, self.dest_port, self.seq_num, data_val)
            return header
        elif self.packet_type == 1 or self.packet_type == 2:
            header = struct.pack(">BHHIB", self.packet_type, self.source_port, self.dest_port, self.seq_num, 0)
            return header
        elif self.packet_type == 3:
            dv_header_part = struct.pack(">BHHI", self.packet_type, self.source_port, self.dest_port, self.seq_num)
            return dv_header_part + self.data # self.data is already bytes (encoded JSON)
        else:
            raise ValueError(f"Unknown packet type in packet_to_bytes: {self.packet_type}")


    def bytes_to_packet(data_bytes):
        if not data_bytes:
            raise ValueError("Cannot decode empty bytes")

        packet_type = struct.unpack(">B", data_bytes[0:1])[0]

        if packet_type == 0 or packet_type == 1 or packet_type == 2: # GBN packets
            if len(data_bytes) != 10:
                raise ValueError(f"Invalid GBN packet length: {len(data_bytes)} bytes, expected 10 for type {packet_type}")
            _, source_port, dest_port, seq_num, data_val = struct.unpack(">BHHIB", data_bytes)

            if packet_type == 0: # GBN Probe
                data = bytes([data_val])
                return Packet(source_port, dest_port, seq_num, packet_type, data)
            else:
                return Packet(source_port, dest_port, seq_num, packet_type, None)

        elif packet_type == 3:
            if len(data_bytes) < 9:
                raise ValueError(f"Invalid DV packet length: {len(data_bytes)} bytes, expected at least 9 for type {packet_type}")
            
            _, source_port, dest_port, seq_num = struct.unpack(">BHHI", data_bytes[0:9])
            json_data_bytes = data_bytes[9:]
            return Packet(source_port, dest_port, seq_num, packet_type, json_data_bytes)

        else:
            raise ValueError(f"unknown packet type in bytes_to_packet: {packet_type}")
