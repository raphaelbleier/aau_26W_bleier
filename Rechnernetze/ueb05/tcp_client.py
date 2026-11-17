# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Erweitere tcp_client.py aus Blatt 05 fuer mehrere Nachrichten
# ueber eine Verbindung, Rohdaten und Laengenpraefix; pruefe die Echo-Bytes.
import argparse
import socket
from framing import recv_frame, send_frame


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="10.0.2.2")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--mode", choices=["framed", "raw"], default="framed")
    p.add_argument("--large", type=int, default=0)
    args = p.parse_args()
    messages = [b"Hello\n", b"from\n", b"Python\n", b"and Mininet!\n"]
    if args.large:
        messages.append(bytes(range(256)) * args.large)
    with socket.create_connection((args.host, args.port), timeout=30) as sock:
        if args.mode == "framed":
            for message in messages:
                send_frame(sock, message)
                if recv_frame(sock) != message:
                    raise AssertionError("Falsches Echo")
            sock.shutdown(socket.SHUT_WR)
        else:
            for message in messages:
                sock.sendall(message)
            sock.shutdown(socket.SHUT_WR)
            reply = bytearray()
            while True:
                part = sock.recv(8192)
                if not part:
                    break
                reply.extend(part)
            if bytes(reply) != b"".join(messages):
                raise AssertionError("Falscher Byte-Stream")
    print("OK", len(messages), "Nachrichten", sum(map(len, messages)), "Nutzbytes")


if __name__ == "__main__":
    main()
