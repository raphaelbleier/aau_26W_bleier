# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Erweitere tcp_server.py aus Blatt 05 um persistente Verbindungen,
# variable recv-Groesse und optionales 4-Byte-Laengenpraefix mit Echo.
import argparse
import json
import socket
from framing import recv_frame, send_frame


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="10.0.2.2")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--recv-size", type=int, default=1024)
    p.add_argument("--mode", choices=["framed", "raw"], default="framed")
    p.add_argument("--once", action="store_true")
    args = p.parse_args()
    if args.recv_size <= 0:
        p.error("recv-size muss positiv sein")
    with socket.socket() as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((args.host, args.port))
        listener.listen(5)
        print("READY", flush=True)
        while True:
            conn, _ = listener.accept()
            with conn:
                conn.settimeout(30)
                while True:
                    data = (recv_frame(conn, args.recv_size) if args.mode == "framed"
                            else conn.recv(args.recv_size))
                    if data is None or (args.mode == "raw" and not data):
                        break
                    print(json.dumps({"bytes": len(data), "head": data[:32].hex()}), flush=True)
                    if args.mode == "framed":
                        send_frame(conn, data)
                    else:
                        conn.sendall(data)
            if args.once:
                break


if __name__ == "__main__":
    main()
