# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.6): „Erweitern Sie das Programm aus Ü 1.5 so, dass alle Threads ein gemeinsames Ergebnis erzeugen. Schützen Sie anschließend den Zugriff auf die gemeinsame Variable mit einem geeigneten Synchronisationsmechanismus aus der Python-Standardbibliothek.“
import argparse
import threading

from threaded_calc import (
    complicated_calculation,
    read_values,
    split_ranges,
    validate_calculation_inputs,
)


def run_shared_sum(values, number_of_threads, use_lock=True, iterations=20000):
    """Addiert Teilergebnisse; ohne Lock macht eine Barriere den Race sichtbar."""
    values = validate_calculation_inputs(values, number_of_threads, iterations)
    if type(use_lock) is not bool:
        raise TypeError("use_lock muss bool sein.")
    ranges = split_ranges(len(values), number_of_threads)
    shared_total = [0.0]
    lock = threading.Lock()
    errors = []
    errors_lock = threading.Lock()
    # Im fehlerhaften Lauf lesen alle Threads zuerst denselben alten Wert.
    read_barrier = threading.Barrier(number_of_threads) if not use_lock else None

    def worker(start, end):
        try:
            partial = sum(
                complicated_calculation(value, iterations) for value in values[start:end]
            )
            if use_lock:
                with lock:
                    shared_total[0] += partial
            else:
                old_value = shared_total[0]
                assert read_barrier is not None
                read_barrier.wait()
                shared_total[0] = old_value + partial
        except BaseException as exc:
            with errors_lock:
                errors.append(exc)
            if read_barrier is not None:
                read_barrier.abort()

    threads = [
        threading.Thread(target=worker, args=range_, name="sum-{}".format(index))
        for index, range_ in enumerate(ranges)
    ]
    started = []
    try:
        for thread in threads:
            thread.start()
            started.append(thread)
    except BaseException:
        if read_barrier is not None:
            read_barrier.abort()
        for thread in started:
            thread.join()
        raise
    for thread in started:
        thread.join()
    if errors:
        raise errors[0]
    return shared_total[0]


def main():
    parser = argparse.ArgumentParser(
        description="Vergleicht gemeinsame Summen mit und ohne Lock."
    )
    parser.add_argument("input_file", help="Datei mit einer Gleitkommazahl pro Zeile")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats <= 0:
        parser.error("repeats muss positiv sein.")
    try:
        values = read_values(args.input_file)
        expected = sum(
            complicated_calculation(value, args.iterations) for value in values
        )
        for attempt in range(1, args.repeats + 1):
            unsafe = run_shared_sum(
                values, args.threads, use_lock=False, iterations=args.iterations
            )
            safe = run_shared_sum(
                values, args.threads, use_lock=True, iterations=args.iterations
            )
            print("Lauf {} ohne Lock: {:.6f}".format(attempt, unsafe))
            print("Lauf {} mit Lock:  {:.6f}".format(attempt, safe))
        print("Soll (sequenziell): {:.6f}".format(expected))
    except Exception as exc:
        parser.exit(1, "Fehler: {}\n".format(exc))


if __name__ == "__main__":
    main()
