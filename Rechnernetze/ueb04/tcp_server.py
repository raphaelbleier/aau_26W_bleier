# KI: Hermes Agent, grok-4.7, 30.10.2026. Anfrage in KI_NUTZUNG.md.
"""Ü 4.6: TCP-Server.

Anfrage: Socket erzeugen, an IP und Port binden, auf Verbindungen warten,
mit accept() annehmen, Daten empfangen und die Verbindung schließen.
Mehrere Nachrichten über dieselbe Verbindung, nicht eine Verbindung pro Satz.
"""
import argparse
import socket


def handle_single(conn):
    """Eine Nutzlast pro Verbindung. Lesen bis der Client den Schreibkanal schließt."""
    chunks = []
    while True:
        data = conn.recv(4096)
        if not data:
            break
        chunks.append(data)
    payload = b"".join(chunks)
    print(f"Received: {payload!r}", flush=True)
    if payload:
        conn.sendall(b"ACK: " + payload)


def handle_lines(conn):
    """Zeilen über eine offene Verbindung. QUIT beendet nur diese Sitzung."""
    reader = conn.makefile("rb")
    try:
        while True:
            line = reader.readline()
            if not line:
                break
            text = line.rstrip(b"\r\n")
            if text == b"QUIT":
                conn.sendall(b"BYE\n")
                break
            print(f"Received: {text!r}", flush=True)
            conn.sendall(b"ACK: " + text + b"\n")
    finally:
        reader.close()


def serve(host, port, multi):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print(f"TCP server listening on {host}:{port}", flush=True)
    try:
        while True:
            conn, address = server.accept()
            print(f"Connection from {address}", flush=True)
            try:
                if multi:
                    handle_lines(conn)
                else:
                    handle_single(conn)
            finally:
                conn.close()
                print(f"Closed {address}", flush=True)
    except KeyboardInterrupt:
        print("Server stopped.", flush=True)
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(description="TCP-Server für Blatt 4")
    parser.add_argument("--host", default="10.0.2.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument(
        "--multi",
        action="store_true",
        help="mehrere Zeilen über dieselbe Verbindung, Ende mit QUIT",
    )
    args = parser.parse_args()
    serve(args.host, args.port, args.multi)


if __name__ == "__main__":
    main()
