# KI: Hermes Agent, grok-4.7, 30.10.2026. Anfrage in KI_NUTZUNG.md.
"""Ü 4.6: TCP-Client.

Anfrage: TCP-Socket erzeugen, Verbindung herstellen, Nachricht senden,
gegebenenfalls Antwort lesen und die Verbindung schließen.
Mit --multi bleiben mehrere Nachrichten auf derselben Verbindung.
"""
import argparse
import socket


def recv_some(sock, limit=4096):
    sock.settimeout(2)
    try:
        return sock.recv(limit)
    except socket.timeout:
        return b""
    finally:
        sock.settimeout(None)


def send_single(host, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        payload = message.encode("utf-8")
        sock.sendall(payload)
        # Schreibseite zu, damit der Server das Ende der einen Nachricht sieht.
        sock.shutdown(socket.SHUT_WR)
        reply = recv_some(sock)
        print(f"Sent {payload!r} to {host}:{port}", flush=True)
        if reply:
            print(f"Reply: {reply!r}", flush=True)
    finally:
        sock.close()


def send_many(host, port, messages):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        for message in messages:
            line = message.encode("utf-8") + b"\n"
            sock.sendall(line)
            reply = recv_some(sock)
            print(f"Sent {message!r}", flush=True)
            if reply:
                print(f"Reply: {reply!r}", flush=True)
        sock.sendall(b"QUIT\n")
        bye = recv_some(sock)
        if bye:
            print(f"Reply: {bye!r}", flush=True)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="TCP-Client für Blatt 4")
    parser.add_argument("--host", default="10.0.2.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--message", action="append", default=None)
    parser.add_argument("--multi", action="store_true")
    args = parser.parse_args()
    messages = args.message or ["Hello from TCP"]
    if args.multi or len(messages) > 1:
        send_many(args.host, args.port, messages)
    else:
        send_single(args.host, args.port, messages[0])


if __name__ == "__main__":
    main()
