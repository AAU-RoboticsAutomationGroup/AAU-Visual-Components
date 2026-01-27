import socket

HOST = "127.0.0.1"
PORT = 2000
BUF = 4096

counter = 0

# Hardcoded responses by (MClass, MNo, #ONo, #OPos)
# Values chosen to look like typical MES4 "standard parameters":
# ResourceID, ONo, OPos, WPNo, OpNo, PNo, StepNo, Parameters :contentReference[oaicite:4]{index=4}
RESPONSES = {
    (100, 4): dict(ResourceID=65, ONo=1550, OPos=1, WPNo=1, OpNo=200, PNo=1214, StepNo=10, Parameters="211-1-3-0"), # Response for GetFirstOpForRsc
    (100, 6): dict(ResourceID=63, ONo=1550, OPos=1, WPNo=1, OpNo=122, PNo=1214, StepNo=20, Parameters="211-1-4-0"), # Response for GetOpForONoOPos
    (101, 10): dict(ResourceID=65, ONo=1550, OPos=1, WPNo=1, OpNo=0, PNo=0, StepNo=0, Parameters="212-0-1-1"),   # Response for OpStart
    (101, 20): dict(ResourceID=65, ONo=1550, OPos=1, WPNo=1, OpNo=200, PNo=1214, StepNo=10, Parameters="212-0-1-1"),   # Response for OpEnd
}

def parse_full_string_request(msg: str) -> dict:
    """
    Parses: '444;RequestId=0;MClass=100;MNo=6;#ONo=1549;#OPos=1\\r'
    Full string encoding uses ';' separated name=value and ends with CR or '*'. :contentReference[oaicite:5]{index=5}
    """
    msg = msg.strip("\r\n*")
    parts = [p for p in msg.split(";") if p]

    out = {}
    if parts:
        out["TcpIdent"] = parts[0]  # first token has no name in MES4 string encoding :contentReference[oaicite:6]{index=6}

    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[p.strip()] = ""

    return out

def make_response(req: dict) -> str:
    global counter
    tcp_ident = req.get("TcpIdent", "444")  # MES4 repeats this in the response :contentReference[oaicite:7]{index=7}
    request_id = req.get("RequestId", "0")
    mclass = int(req.get("MClass", "0") or 0)
    mno = int(req.get("MNo", "0") or 0)
    ono = int(req.get("#ONo", "0") or 0)
    opos = int(req.get("#OPos", "0") or 0)

    # Only emulate the service you are currently using:
    message_type = [mclass, mno]
    data = None

    match message_type:
        case [100, 4]:  # GetFirstOpForRsc
            if counter <= 2:
                counter += 1
                data = RESPONSES.get((mclass, mno))
                ono = data["ONo"] if data else ono
                opos = data["OPos"] if data else opos
            else:
                return (
                    f"{tcp_ident};RequestId={request_id};MClass={mclass};MNo={mno};"
                    f"ErrorState=0;"
                    f"ResourceID=0;ONo={ono};OPos={opos};WPNo=0;OpNo=0;PNo=0;StepNo=0;Parameters=\r"
                )

        case [100, 6]:  # GetOpForONoOPos
            data = RESPONSES.get((mclass, mno))

        case [101, 10]:  # OpStart
            data = RESPONSES.get((mclass, mno))

        case [101, 20]:  # OpEnd
            data = RESPONSES.get((mclass, mno))

            # Update step... e.g.
            #RESPONSES[(101, 20, ono, opos)] = dict(ResourceID=data["ResourceID"],
            #                                      WPNo=data["WPNo"],
            #                                      OpNo=data["OpNo"],
            #                                      PNo=data["PNo"],
            #                                      StepNo=data["StepNo"] + 10,
            #                                      Parameters=data["Parameters"])

        case _:
            # Generic fallback for any other service call
            return f"{tcp_ident};RequestId={request_id};MClass={mclass};MNo={mno};ErrorState=0\r"
        
    if data:
        return (
            f"{tcp_ident};RequestId={request_id};MClass={mclass};MNo={mno};"
            f"ErrorState=0;"
            f"ResourceID={data['ResourceID']};"
            f"ONo={ono};OPos={opos};"
            f"WPNo={data['WPNo']};"
            f"OpNo={data['OpNo']};"
            f"PNo={data['PNo']};"
            f"StepNo={data['StepNo']};"
            f"Parameters={data['Parameters']}\r"
        )
    else:    
        # "Not found" but still validly formatted response
        return (
            f"{tcp_ident};RequestId={request_id};MClass={mclass};MNo={mno};"
            f"ErrorState=0;"
            f"ResourceID=0;ONo={ono};OPos={opos};WPNo=0;OpNo=0;PNo=0;StepNo=0;Parameters=\r"
        )

def serve_forever():
    print(f"MES4 emulator listening on {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(10)

        while True:
            conn, addr = s.accept()
            with conn:
                raw = conn.recv(BUF)
                if not raw:
                    continue
                msg = raw.decode("ascii", errors="replace")
                print(f"[{addr}] RX: {msg!r}")

                req = parse_full_string_request(msg)
                resp = make_response(req)

                print(f"[{addr}] TX: {resp!r}")
                conn.sendall(resp.encode("ascii", errors="replace"))

if __name__ == "__main__":
    serve_forever()
