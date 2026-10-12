# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.5): „Implementieren Sie ein Programm, das eine Liste von Gleitkommazahlen aus einer Datei liest und eine rechenintensive Funktion auf den Werten ausführt. Die Berechnung soll auf n Threads aufgeteilt werden.“
import argparse
import math
import threading
from pathlib import Path


def read_values(path):
    """Liest pro nichtleerer Zeile eine Gleitkommazahl."""
    values = []
    with Path(path).open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                values.append(float(stripped))
            except ValueError as exc:
                raise ValueError(
                    "Ungültige Zahl in Zeile {}: {!r}".format(line_number, stripped)
                ) from exc
    return values


def split_ranges(length, number_of_threads):
    """Teilt auch dann vollständig auf, wenn die Länge nicht durch n teilbar ist."""
    if length < 0:
        raise ValueError("length darf nicht negativ sein.")
    if number_of_threads <= 0:
        raise ValueError("number_of_threads muss positiv sein.")
    base, remainder = divmod(length, number_of_threads)
    ranges = []
    start = 0
    for index in range(number_of_threads):
        size = base + (1 if index < remainder else 0)
        end = start + size
        ranges.append((start, end))
        start = end
    return ranges


def complicated_calculation(value, iterations=20000):
    """Eine reproduzierbare Rechenaufgabe, die pro Array-Wert Arbeit erzeugt."""
    if iterations <= 0:
        raise ValueError("iterations muss positiv sein.")
    basis = abs(value)
    return sum(math.sqrt(basis + index + 1) for index in range(iterations))


def validate_calculation_inputs(values, number_of_threads, iterations):
    if isinstance(number_of_threads, bool) or not isinstance(number_of_threads, int):
        raise TypeError("number_of_threads muss eine Ganzzahl sein.")
    if number_of_threads <= 0:
        raise ValueError("number_of_threads muss positiv sein.")
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise TypeError("iterations muss eine Ganzzahl sein.")
    if iterations <= 0:
        raise ValueError("iterations muss positiv sein.")
    values = list(values)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        raise TypeError("Alle Werte müssen Integer oder Gleitkommazahlen sein.")
    return values


def calculate_parallel(values, number_of_threads, iterations=20000):
    values = validate_calculation_inputs(values, number_of_threads, iterations)
    ranges = split_ranges(len(values), number_of_threads)
    results = [None] * number_of_threads
    errors = []
    errors_lock = threading.Lock()

    def worker(start, end, index):
        try:
            results[index] = sum(
                complicated_calculation(value, iterations) for value in values[start:end]
            )
        except BaseException as exc:
            with errors_lock:
                errors.append(exc)

    threads = [
        threading.Thread(target=worker, args=(start, end, index), name="calc-{}".format(index))
        for index, (start, end) in enumerate(ranges)
    ]
    started = []
    try:
        for thread in threads:
            thread.start()
            started.append(thread)
    except BaseException:
        for thread in started:
            thread.join()
        raise
    for thread in started:
        thread.join()
    if errors:
        raise errors[0]
    return sum(results)


def main():
    parser = argparse.ArgumentParser(
        description="Berechnet Dateiwerte auf mehrere Threads verteilt."
    )
    parser.add_argument("input_file", help="Datei mit einer Gleitkommazahl pro Zeile")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=20000)
    args = parser.parse_args()
    try:
        values = read_values(args.input_file)
        result = calculate_parallel(values, args.threads, args.iterations)
    except Exception as exc:
        parser.exit(1, "Fehler: {}\n".format(exc))
    print("Werte: {}".format(len(values)))
    print("Threads: {}".format(args.threads))
    print("Ergebnis: {:.6f}".format(result))


if __name__ == "__main__":
    main()
