# KI: Hermes Agent, grok-4.7, 30.10.2026. Anfrage in KI_NUTZUNG.md.
"""Ü 4.3: UDP-Server aus der Angabe.

Anfrage: Server an 10.0.0.2:5000 binden, Datagramme empfangen und
Absender plus Nutzlast ausgeben.
"""
import argparse
import socket


def main():
    parser = argparse.ArgumentParser(description="UDP-Server für Blatt 4")
    parser.add_argument("--host", default="10.0.0.2")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # SO_REUSEADDR, damit ein Neustart nach einem Test nicht am alten Port hängt.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    print(f"Server listening on {args.host}:{args.port}", flush=True)
    try:
        while True:
            data, address = server.recvfrom(4096)
            print(f"Received from {address}: {data!r}", flush=True)
    except KeyboardInterrupt:
        print("Server stopped.", flush=True)
    finally:
        server.close()


if __name__ == "__main__":
    main()
