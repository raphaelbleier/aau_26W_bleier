# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.7): „Verwenden Sie hierfür queue.Queue aus der Python-Standardbibliothek. Die Queue soll eine begrenzte Größe besitzen, sodass der Producer gegebenenfalls warten muss, wenn der Container voll ist.“
import argparse
import queue
import threading


def produce_consume(values, queue_size=4):
    """Liefert Werte über eine begrenzte Queue an genau einen Consumer."""
    if queue_size <= 0:
        raise ValueError("queue_size muss positiv sein.")
    values = list(values)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("Alle Queue-Werte müssen Integer sein.")
    work_queue = queue.Queue(maxsize=queue_size)
    stop = object()
    stop_event = threading.Event()
    received = []
    result = [0]
    errors = []
    errors_lock = threading.Lock()

    def record_error(exc):
        with errors_lock:
            errors.append(exc)
        stop_event.set()

    def put_item(item):
        while not stop_event.is_set():
            try:
                work_queue.put(item, timeout=0.05)
                return True
            except queue.Full:
                continue
        return False

    def producer():
        try:
            for value in values:
                if not put_item(value):
                    return
            put_item(stop)
        except BaseException as exc:
            record_error(exc)

    def consumer():
        try:
            while not stop_event.is_set():
                try:
                    item = work_queue.get(timeout=0.05)
                except queue.Empty:
                    continue
                try:
                    if item is stop:
                        return
                    if isinstance(item, bool) or not isinstance(item, int):
                        raise TypeError("Die Queue enthält einen unerwarteten Wert.")
                    received.append(item)
                    result[0] += item
                finally:
                    work_queue.task_done()
        except BaseException as exc:
            record_error(exc)

    consumer_thread = threading.Thread(target=consumer, name="consumer")
    producer_thread = threading.Thread(target=producer, name="producer")
    started = []
    try:
        for thread in (consumer_thread, producer_thread):
            thread.start()
            started.append(thread)
    except BaseException:
        stop_event.set()
        for thread in started:
            thread.join()
        raise

    for thread in started:
        thread.join()
    if errors:
        raise errors[0]
    work_queue.join()
    return received, result[0]


def main():
    parser = argparse.ArgumentParser(
        description="Producer-Consumer mit begrenzter Queue."
    )
    parser.add_argument("--count", type=int, default=20, help="Integer von 1 bis count erzeugen")
    parser.add_argument("--queue-size", type=int, default=4)
    args = parser.parse_args()
    if args.count < 0:
        parser.error("count darf nicht negativ sein.")
    try:
        received, total = produce_consume(range(1, args.count + 1), args.queue_size)
    except Exception as exc:
        parser.exit(1, "Fehler: {}\n".format(exc))
    print("Empfangen: {}".format(received))
    print("Summe: {}".format(total))


if __name__ == "__main__":
    main()
