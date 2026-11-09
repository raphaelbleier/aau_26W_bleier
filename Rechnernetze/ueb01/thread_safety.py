

import argparse
import threading

from threaded_calc import (
    complicated_calculation,
    read_values,
    split_ranges,
    validate_calculation_inputs,
)


def run_shared_sum(
    values, number_of_threads, use_lock=True, iterations=20000, force_lost_update=False
):
    """Addiert Teilergebnisse direkt oder geschützt; ein Kontrolllauf erzwingt das Rennen."""
    values = validate_calculation_inputs(values, number_of_threads, iterations)
    if type(use_lock) is not bool:
        raise TypeError("use_lock muss bool sein.")
    if type(force_lost_update) is not bool:
        raise TypeError("force_lost_update muss bool sein.")
    if use_lock and force_lost_update:
        raise ValueError("force_lost_update funktioniert nur ohne Lock.")
    ranges = split_ranges(len(values), number_of_threads)
    shared_total = [0.0]
    lock = threading.Lock()
    errors = []
    errors_lock = threading.Lock()
    # Der Kontrolllauf liest absichtlich vor einer Barriere denselben alten Wert.
    read_barrier = threading.Barrier(number_of_threads) if force_lost_update else None

    def worker(start, end):
        try:
            partial = sum(
                complicated_calculation(value, iterations) for value in values[start:end]
            )
            if use_lock:
                with lock:
                    shared_total[0] += partial
            elif force_lost_update:
                old_value = shared_total[0]
                assert read_barrier is not None
                read_barrier.wait()
                shared_total[0] = old_value + partial
            else:
                shared_total[0] += partial
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
            controlled = run_shared_sum(
                values, args.threads, use_lock=False,
                iterations=args.iterations, force_lost_update=True
            )
            print("Lauf {} direkt ohne Lock: {:.6f}".format(attempt, unsafe))
            print("Lauf {} mit Lock:          {:.6f}".format(attempt, safe))
            print("Kontrolllauf mit Barriere: {:.6f}".format(controlled))
        print("Soll (sequenziell): {:.6f}".format(expected))
    except Exception as exc:
        parser.exit(1, "Fehler: {}\n".format(exc))


if __name__ == "__main__":
    main()
