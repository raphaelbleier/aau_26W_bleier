# KI: Hermes Agent, grok-4.7, 30.10.2026. Anfrage in KI_NUTZUNG.md.
"""Ü 4.3: UDP-Client aus der Angabe.

Anfrage: Ein Datagramm an den Server schicken. Bytes, nicht str,
weil sendto eine Bytefolge erwartet.
"""
import argparse
import socket


def main():
    parser = argparse.ArgumentParser(description="UDP-Client für Blatt 4")
    parser.add_argument("--host", default="10.0.0.2")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--message", default="Hello from Mininet!")
    args = parser.parse_args()

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = args.message.encode("utf-8")
    client.sendto(payload, (args.host, args.port))
    print(f"Sent {payload!r} to {args.host}:{args.port}", flush=True)
    client.close()


if __name__ == "__main__":
    main()
