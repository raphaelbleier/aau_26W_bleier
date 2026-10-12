# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.2): „Erstellen Sie ein Programm, das eine Zeichenkette einliest und diese zunächst als UTF-8 in Bytes kodiert. Geben Sie anschließend sowohl die Zeichenkette als auch die Bytefolge aus. Erweitern Sie das Programm, dass die Bytefolge wieder in eine Zeichenkette dekodiert wird.“
import argparse


def round_trip(text):
    """Kodiert Text als UTF-8 und dekodiert dieselben Bytes wieder."""
    if not isinstance(text, str):
        raise TypeError("text muss eine Zeichenkette sein.")
    data = text.encode("utf-8")
    return data, data.decode("utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Zeigt den Unterschied zwischen str und bytes."
    )
    parser.add_argument("--text", help="Text; wenn nicht gesetzt, wird eine Eingabe abgefragt")
    args = parser.parse_args()
    text = args.text if args.text is not None else input("Text: ")
    data, decoded = round_trip(text)
    print("str: {}".format(text))
    print("bytes: {}".format(data))
    print("len(str): {}".format(len(text)))
    print("len(bytes): {}".format(len(data)))
    print("dekodiert: {}".format(decoded))


if __name__ == "__main__":
    main()
