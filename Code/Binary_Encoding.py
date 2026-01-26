import struct
import socket

MES4_IP = "172.20.0.90"   # change to MES4 PC IP
MES4_PORT = 2001          # change to MES4 port
BUFFER_SIZE = 1024

# Create an empty 84-byte header
header = bytearray(84)

def write_int16(offset, value):
    struct.pack_into("<h", header, offset, value)

def write_int32(offset, value):
    struct.pack_into("<i", header, offset, value)

# ---- Mandatory / typical fields ----

write_int32(0, 1)      # TcpIdent (DINT)
write_int16(4, 99)    # RequestID (omitted if not a resource)
write_int16(6, 100)    # MClass
write_int16(8, 30)     # MNo (example: depends on MES command)
write_int16(10, 0)     # ErrorState
write_int16(12, 0)     # DataLength (no payload)¨
#write_int16(14, 63)   # ResourceID
write_int32(16, 1542)  # Order number
write_int16(20, 1)     # Order position


# ---- Example workplan-related parameters ----
write_int16(22, 0)     # #WPNo (Workplan number)
write_int16(24, 0)     # #OpNo (Operation number)
write_int16(46, 0)     # #MaxRecords

# Everything else remains 0

# Convert to bytes for sending
message = bytes(header)

print("Header length:", len(message))
print("Raw bytes:", message.hex())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((MES4_IP, MES4_PORT))

    sock.sendall(message)

    response = sock.recv(BUFFER_SIZE)

    print(response)