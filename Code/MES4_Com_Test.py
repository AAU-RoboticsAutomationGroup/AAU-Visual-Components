import socket

MES4_IP = "172.20.0.90"   # change to MES4 PC IP
MES4_PORT = 2000           # change to MES4 port
BUFFER_SIZE = 1024

def hex_colon_to_ascii(hex_string: str) -> str:
    """
    Convert '48:65:6C:6C:6F:00' → 'Hello'
    """
    bytes_data = bytes(int(b, 16) for b in hex_string.split(":"))
    return bytes_data.decode("ascii").rstrip("\x00")

def send_mes4_command(command: str):
    """
    Send an ASCII command to MES4 and return raw + decoded response.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MES4_IP, MES4_PORT))

        # MES4 often expects null-terminated strings
        message = command.encode("ascii") + b"\x00"

        print(f"Sending: {command}")
        sock.sendall(message)

        response = sock.recv(BUFFER_SIZE)

        print("Raw bytes:", response)
        try:
            decoded = response.decode("ascii").rstrip("\x00")
            print("Decoded:", decoded)
        except UnicodeDecodeError:
            print("Could not decode response as ASCII")

        return response


if __name__ == "__main__":
    send_mes4_command("444;RequestId=62;MClass=100;MNo=33;#ONo=1;#OPos=1*")