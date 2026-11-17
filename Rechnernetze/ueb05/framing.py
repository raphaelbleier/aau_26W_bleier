# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Implementiere Blatt 05, TCP-Byte-Stream mit 4-Byte-Laengenpraefix,
# begrenzter Framegroesse und Tests fuer fragmentierte und gebuendelte Daten.
"""Nachrichten mit vier Byte Länge in Netzwerk-Bytefolge."""
import struct

MAX_FRAME = 4 * 1024 * 1024


def recv_exact(sock, size, chunk_size=1024, allow_eof=False):
    if chunk_size <= 0 or size < 0:
        raise ValueError("Ungueltige Empfangsgroesse")
    data = bytearray()
    while len(data) < size:
        part = sock.recv(min(chunk_size, size - len(data)))
        if not part:
            if allow_eof and not data:
                return None
            raise EOFError("Verbindung mitten im Frame geschlossen")
        data.extend(part)
    return bytes(data)


def send_frame(sock, payload):
    if len(payload) > MAX_FRAME:
        raise ValueError("Frame zu gross")
    sock.sendall(struct.pack("!I", len(payload)) + payload)


def recv_frame(sock, chunk_size=1024):
    header = recv_exact(sock, 4, chunk_size, allow_eof=True)
    if header is None:
        return None
    length, = struct.unpack("!I", header)
    if length > MAX_FRAME:
        raise ValueError("Frame zu gross")
    return recv_exact(sock, length, chunk_size)
