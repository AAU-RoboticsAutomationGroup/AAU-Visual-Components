"""
The following code can be used to communicate with MES4. It consist of two communication parts:
    1. Cyclic connection message:
       If a resource with the PC's IP is created in MES4 this message ensures that the MES4 sees the script as a connected resource

    2. Operation request:
       This part requests MES4 for operation infomration using the string messages.


Link with MES4 interface description:
https://ftp.festo.com/public/DIDACTIC/MES4/Tools/MES4_Interface_en_v1.07.pdf
"""

import struct
import socket
import time

MES4_IP = "172.20.0.90"      # change to MES4 PC IP
MES4_PORT_CYC = 2001         # change to MES4 port
MES4_PORT_SERVICE = 2000     # change to MES4 port
BUFFER_SIZE = 2048

msg_service = bytearray(128)

# The following functions are not used but can be used for more efficient communication with MES4. Now string messages are used.
def write_int16(offset, value):
    struct.pack_into("<H", msg_service, offset, value)  # "<"=little endian, H=unsigned 16-bit integer

def write_int32(offset, value):
    struct.pack_into("<I", msg_service, offset, value)  # "<"=little endian, I=unsigned 32-bit integer

def write_uint8(offset, value):
    struct.pack_into("<B", msg_service, offset, value)  # "<"=little endian, B=unsigned 8-bit integer

def make_status_byte(
    bit0=False,
    bit1=False,
    bit2=False,
    bit3=False,
    bit4=False,
    bit5=False,
    bit6=False,
    bit7=False,
):
    value = 0
    value |= int(bit0) << 0
    value |= int(bit1) << 1
    value |= int(bit2) << 2
    value |= int(bit3) << 3
    value |= int(bit4) << 4
    value |= int(bit5) << 5
    value |= int(bit6) << 6
    value |= int(bit7) << 7
    return value


# Create the cyclic update message for the PC
msg_cyclic = bytearray(4)
struct.pack_into("<H", msg_cyclic, 0, 99)   # ResourceID (must match with MES4)
struct.pack_into("<B", msg_cyclic, 2, 1)    # PLC Type (1=little endian (CodeSys))
status_byte = make_status_byte(0,0,0,0,0,0,0,1)     #Status indicator for being in MES-mode
struct.pack_into("<B", msg_cyclic, 3, status_byte)  # Status byte

# Convert to bytes for sending
message_update = bytes(msg_cyclic)


# The following is not used
# Create the service request - request for order info
write_int32(0, 1)      # TcpIdent (DINT) (1=CodeSys)
write_int16(4, 99)    # RequestID (omitted if not a resource)
write_int16(6, 100)    # MClass
write_int16(8, 30)     # MNo (example: depends on MES command)
write_int16(10, 0)     # ErrorState
write_int16(12, 0)     # DataLength (no payload)¨
write_int16(14, 0)   # ResourceID
write_int32(16, 1546)  # Order number
write_int16(20, 0)     # Order position

# ---- Example workplan-related parameters ----
write_int16(22, 0)     # #WPNo (Workplan number)
write_int16(24, 0)     # #OpNo (Operation number)
write_int16(44, 0)     # #Step number
write_int16(46, 0)     # #MaxRecords

# Convert to bytes for sending
message_service = bytes(msg_service)

print("Header length:", len(message_service))
print("Raw bytes:", message_service.hex())

# Alternative request example (Used)

#msg = "444;RequestId=99;MClass=100;MNo=30;#ONo=1546" # Does order exist? 
#msg = "444;RequestId=99;MClass=100;MNo=33;#ONo=1546;#OPos=1" # Get step description
# msg = "444;RequestId=99;MClass=100;MNo=4;#ResourceID=65" # Gives back the first task of an order for a specific resource.
msg = "444;RequestId=0;MClass=100;MNo=6;#ONo=1549;#OPos=1" # Gives back the task details for a specific order

# Comment in to send updates
#sock_cyclic = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock_cyclic.connect((MES4_IP, MES4_PORT_CYC))

sock_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_srv.connect((MES4_IP, MES4_PORT_SERVICE))

while True:
    # Comment in to send cyclic update message
    #sock_cyclic.sendall(message_update)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MES4_IP, MES4_PORT_SERVICE))
        sock_srv.sendall(msg.encode("ascii")+b"\r")
        time.sleep(0.5)
        response = sock_srv.recv(BUFFER_SIZE)
        print(response)

    sock_srv.sendall(msg.encode("ascii")+b"\r")
    time.sleep(0.5)
    response = sock_srv.recv(BUFFER_SIZE)
    print(response)

    time.sleep(1)