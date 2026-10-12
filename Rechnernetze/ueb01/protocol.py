# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.4): „Die Nachricht besteht aus einem Versionsfeld V mit 5 Bit (fixer Wert 2), 9 reservierten Bits (immer 0), zwei Flags D und U, einer 16 Bit großen Sequenznummer und einer 32 Bit großen Payload-Länge. Anschließend folgt die eigentliche Nutzlast variabler Länge. Implementieren Sie eine Funktion create_message(is_data, is_urgent, sequence_number, payload), die eine solche Nachricht als bytes-Objekt erzeugt. Schreiben Sie außerdem eine zweite Funktion parse_message(message).“
import argparse
import struct

VERSION = 2
VERSION_SHIFT = 27
DATA_SHIFT = 17
URGENT_SHIFT = 16
RESERVED_SHIFT = 18
HEADER_FORMAT = "!II"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def _validate_fields(is_data, is_urgent, sequence_number, payload):
    if type(is_data) is not bool or type(is_urgent) is not bool:
        raise TypeError("is_data und is_urgent müssen bool sein.")
    if isinstance(sequence_number, bool) or not isinstance(sequence_number, int):
        raise TypeError("sequence_number muss eine Ganzzahl sein.")
    if not 1 <= sequence_number <= 0xFFFF:
        raise ValueError("sequence_number muss zwischen 1 und 65535 liegen.")
    if not isinstance(payload, bytes):
        raise TypeError("payload muss bytes sein.")
    if not payload:
        raise ValueError("payload darf nicht leer sein.")
    if len(payload) > 0xFFFFFFFF:
        raise ValueError("payload ist zu lang für das 32-Bit-Längenfeld.")


def create_message(is_data, is_urgent, sequence_number, payload):
    """Erzeugt Header und Payload in Network Byte Order (Big Endian)."""
    _validate_fields(is_data, is_urgent, sequence_number, payload)
    header = (
        (VERSION << VERSION_SHIFT)
        | (int(is_data) << DATA_SHIFT)
        | (int(is_urgent) << URGENT_SHIFT)
        | sequence_number
    )
    return struct.pack(HEADER_FORMAT, header, len(payload)) + payload


def parse_message(message):
    """Liest eine Nachricht und weist fehlerhafte Header und Längen zurück."""
    if not isinstance(message, bytes):
        raise TypeError("message muss bytes sein.")
    if len(message) < HEADER_SIZE:
        raise ValueError("Nachricht ist kürzer als der Header.")

    header, payload_length = struct.unpack_from(HEADER_FORMAT, message)
    version = (header >> VERSION_SHIFT) & 0x1F
    reserved = (header >> RESERVED_SHIFT) & 0x1FF
    is_data = bool((header >> DATA_SHIFT) & 1)
    is_urgent = bool((header >> URGENT_SHIFT) & 1)
    sequence_number = header & 0xFFFF
    payload = message[HEADER_SIZE:]

    if version != VERSION:
        raise ValueError("Unbekannte Versionsnummer.")
    if reserved != 0:
        raise ValueError("Reservierte Bits müssen 0 sein.")
    if sequence_number == 0:
        raise ValueError("sequence_number muss positiv sein.")
    if payload_length == 0:
        raise ValueError("payload darf nicht leer sein.")
    if len(payload) != payload_length:
        raise ValueError("Payload-Längenfeld stimmt nicht mit der Nachricht überein.")
    return is_data, is_urgent, sequence_number, payload


def main():
    parser = argparse.ArgumentParser(
        description="Kleiner Round-trip-Test für das binäre Nachrichtenformat."
    )
    parser.add_argument("--text", default="Hallo Netzwerk!")
    parser.add_argument("--sequence", type=int, default=1)
    parser.add_argument("--data", action="store_true")
    parser.add_argument("--urgent", action="store_true")
    args = parser.parse_args()
    message = create_message(
        args.data, args.urgent, args.sequence, args.text.encode("utf-8")
    )
    print("Nachricht (hex): {}".format(message.hex()))
    print("Felder: {}".format(parse_message(message)))


if __name__ == "__main__":
    main()
