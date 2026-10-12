# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.3): „Schreiben Sie ein Python-Programm convert.py, welches den Namen einer Eingabedatei und den Namen einer Ausgabedatei als Kommandozeilenparameter erhält. Die Eingabedatei enthält einen UTF-8-kodierten Text. Lesen Sie die Datei ein und schreiben Sie den Inhalt in eine neue UTF-8-kodierte Datei. Zeilenumbrüche sollen dabei unabhängig vom auf dem Betriebssystem verwendeten Zeilenende korrekt verarbeitet werden.“
import argparse
from pathlib import Path


def convert_file(input_path, output_path):
    """Kopiert UTF-8-Text und vereinheitlicht Zeilenenden auf LF."""
    source = Path(input_path)
    destination = Path(output_path)
    if source.resolve() == destination.resolve():
        raise ValueError("Eingabe- und Ausgabedatei müssen verschieden sein.")

    # newline=None liest LF, CRLF und CR einheitlich als \n ein.
    with source.open("r", encoding="utf-8", newline=None) as infile:
        content = infile.read()
    # newline="\n" schreibt auf jedem Betriebssystem dieselben Zeilenenden.
    with destination.open("w", encoding="utf-8", newline="\n") as outfile:
        outfile.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Kopiert eine UTF-8-Textdatei mit einheitlichen Zeilenenden."
    )
    parser.add_argument("input_file", help="Eingabedatei")
    parser.add_argument("output_file", help="Ausgabedatei")
    args = parser.parse_args()
    try:
        convert_file(args.input_file, args.output_file)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, "Fehler: {}\n".format(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
