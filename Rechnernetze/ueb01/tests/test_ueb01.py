# KI-Nutzung: Hermes Agent, OpenAI GPT-6 Luna (gpt-6-luna), 2026-10-12.
# Verwendete Anfrage (Auszug aus Übung 1.4): „Testen Sie Ihre Implementierung mit gültigen und ungültigen Eingaben.“
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import hello
import text_bytes
import convert
import protocol
import threaded_calc
import thread_safety
import producer_consumer


class HelloTests(unittest.TestCase):
    def test_report_contains_name_version_and_working_directory(self):
        report = hello.build_report("Raphael Bleier", "3.8.5", "/tmp/demo")
        self.assertIn("Raphael Bleier", report)
        self.assertIn("3.8.5", report)
        self.assertIn("/tmp/demo", report)


class TextBytesTests(unittest.TestCase):
    def test_utf8_round_trip_preserves_umlauts_and_reports_byte_length(self):
        text = "Grüße aus Klagenfurt 🌐"
        encoded, decoded = text_bytes.round_trip(text)
        self.assertEqual(encoded, text.encode("utf-8"))
        self.assertEqual(decoded, text)
        self.assertGreater(len(encoded), len(text))


class ConvertTests(unittest.TestCase):
    def test_conversion_normalizes_mixed_line_endings_to_lf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "in.txt"
            destination = Path(directory) / "out.txt"
            source.write_bytes("eins\r\nzwei\rdrei\n".encode("utf-8"))
            convert.convert_file(source, destination)
            self.assertEqual(destination.read_bytes(), "eins\nzwei\ndrei\n".encode("utf-8"))

    def test_missing_input_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                convert.convert_file(Path(directory) / "missing.txt", Path(directory) / "out.txt")

    def test_permission_error_is_reported(self):
        with mock.patch.object(Path, "open", side_effect=PermissionError("not readable")):
            with self.assertRaises(PermissionError):
                convert.convert_file("input.txt", "output.txt")

    def test_invalid_utf8_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.txt"
            destination = Path(directory) / "out.txt"
            source.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                convert.convert_file(source, destination)

    def test_output_directory_is_reported_as_write_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "in.txt"
            source.write_text("Daten", encoding="utf-8")
            with self.assertRaises(OSError):
                convert.convert_file(source, Path(directory))

    def test_same_input_and_output_path_is_rejected_without_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "same.txt"
            path.write_text("Daten", encoding="utf-8")
            with self.assertRaises(ValueError):
                convert.convert_file(path, path)
            self.assertEqual(path.read_text(encoding="utf-8"), "Daten")

    def test_missing_command_line_parameters_are_rejected(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "convert.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr.lower())


class ProtocolTests(unittest.TestCase):
    def test_create_and_parse_round_trip(self):
        payload = b"Hallo\x00Welt"
        message = protocol.create_message(True, False, 42, payload)
        self.assertEqual(message, bytes.fromhex("1002002a0000000a") + payload)
        self.assertEqual(protocol.parse_message(message), (True, False, 42, payload))

    def test_all_flag_combinations_and_max_sequence_number(self):
        for is_data in (False, True):
            for is_urgent in (False, True):
                with self.subTest(is_data=is_data, is_urgent=is_urgent):
                    message = protocol.create_message(is_data, is_urgent, 65535, b"x")
                    self.assertEqual(
                        protocol.parse_message(message),
                        (is_data, is_urgent, 65535, b"x"),
                    )

    def test_invalid_flags_sequence_and_empty_payload_are_rejected(self):
        with self.assertRaises(TypeError):
            protocol.create_message(1, False, 1, b"x")
        with self.assertRaises(ValueError):
            protocol.create_message(False, False, 0, b"x")
        with self.assertRaises(ValueError):
            protocol.create_message(False, False, 1, b"")
        with self.assertRaises(ValueError):
            protocol.create_message(False, False, 65536, b"x")

    def test_malformed_header_and_payload_length_are_rejected(self):
        with self.assertRaises(ValueError):
            protocol.parse_message(b"short")
        message = protocol.create_message(False, True, 1, b"payload")
        with self.assertRaises(ValueError):
            protocol.parse_message(message[:-1])
        with self.assertRaises(ValueError):
            protocol.parse_message(message + b"extra")
        header = int.from_bytes(message[:4], byteorder="big")
        zero_sequence = (header & 0xFFFF0000).to_bytes(4, byteorder="big") + message[4:]
        with self.assertRaises(ValueError):
            protocol.parse_message(zero_sequence)
        empty_payload = message[:4] + b"\x00\x00\x00\x00"
        with self.assertRaises(ValueError):
            protocol.parse_message(empty_payload)

    def test_nonzero_reserved_bits_and_wrong_version_are_rejected(self):
        message = protocol.create_message(False, False, 1, b"x")
        header = int.from_bytes(message[:4], byteorder="big")
        for bit in range(9):
            with self.subTest(reserved_bit=bit):
                corrupt_header = header | (1 << (18 + bit))
                corrupted = corrupt_header.to_bytes(4, byteorder="big") + message[4:]
                with self.assertRaises(ValueError):
                    protocol.parse_message(corrupted)
        wrong_version = (header ^ (1 << 27)).to_bytes(4, byteorder="big") + message[4:]
        with self.assertRaises(ValueError):
            protocol.parse_message(wrong_version)


class ThreadedCalculationTests(unittest.TestCase):
    def test_reads_float_values_from_file_and_reports_invalid_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "values.txt"
            path.write_text("1.5\n\n-2\n3.25\n", encoding="utf-8")
            self.assertEqual(threaded_calc.read_values(path), [1.5, -2.0, 3.25])
            path.write_text("1.5\nnot-a-number\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Zeile 2"):
                threaded_calc.read_values(path)

    def test_uneven_chunks_match_sequential_result(self):
        values = [1.25, -2.0, 4.5, 8.0, 3.0]
        self.assertAlmostEqual(
            threaded_calc.calculate_parallel(values, 3, iterations=12),
            sum(threaded_calc.complicated_calculation(v, 12) for v in values),
        )

    def test_more_threads_than_values_and_empty_input(self):
        self.assertAlmostEqual(
            threaded_calc.calculate_parallel([2.0], 5, iterations=4),
            threaded_calc.complicated_calculation(2.0, 4),
        )
        self.assertEqual(threaded_calc.calculate_parallel([], 3, iterations=4), 0.0)

    def test_nonpositive_thread_count_is_rejected(self):
        with self.assertRaises(ValueError):
            threaded_calc.calculate_parallel([1.0], 0, iterations=2)

    def test_nonpositive_iterations_fail_before_starting_workers(self):
        for iterations in (0, -1):
            with self.subTest(iterations=iterations):
                with self.assertRaises(ValueError):
                    threaded_calc.calculate_parallel([1.0], 2, iterations=iterations)

    def test_worker_exception_is_propagated(self):
        with mock.patch.object(
            threaded_calc, "complicated_calculation", side_effect=RuntimeError("worker failed")
        ):
            with self.assertRaisesRegex(RuntimeError, "worker failed"):
                threaded_calc.calculate_parallel([1.0, 2.0], 2, iterations=2)

    def test_partial_thread_start_failure_joins_started_workers(self):
        script = (
            "import threading\n"
            "from unittest import mock\n"
            "import threaded_calc\n"
            "original_start = threading.Thread.start\n"
            "starts = [0]\n"
            "def fail_second_start(thread):\n"
            "    starts[0] += 1\n"
            "    if starts[0] == 2:\n"
            "        raise RuntimeError('cannot start new thread')\n"
            "    return original_start(thread)\n"
            "with mock.patch.object(threading.Thread, 'start', new=fail_second_start):\n"
            "    try:\n"
            "        threaded_calc.calculate_parallel([1.0, 2.0], 2, iterations=2)\n"
            "    except RuntimeError as exc:\n"
            "        assert str(exc) == 'cannot start new thread'\n"
            "    else:\n"
            "        raise SystemExit(1)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_iterations_make_cli_exit_nonzero_without_thread_traceback(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "threaded_calc.py"),
                str(ROOT / "zahlen.txt"),
                "--threads",
                "3",
                "--iterations",
                "0",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Fehler:", result.stderr)
        self.assertNotIn("Exception in thread", result.stderr)


class ThreadSafetyTests(unittest.TestCase):
    def test_lock_preserves_total_and_unsafe_update_loses_contributions(self):
        values = [float(i) for i in range(1, 9)]
        expected = sum(threaded_calc.complicated_calculation(v, 5) for v in values)
        for attempt in range(5):
            with self.subTest(attempt=attempt):
                safe = thread_safety.run_shared_sum(values, 4, use_lock=True, iterations=5)
                unsafe = thread_safety.run_shared_sum(values, 4, use_lock=False, iterations=5)
                self.assertAlmostEqual(safe, expected)
                self.assertLess(unsafe, expected)

    def test_invalid_iterations_and_values_fail_before_barrier(self):
        with self.assertRaises(ValueError):
            thread_safety.run_shared_sum([1.0], 2, use_lock=False, iterations=0)
        with self.assertRaises(TypeError):
            thread_safety.run_shared_sum([1.0, "bad"], 2, use_lock=False, iterations=2)

    def test_worker_exception_aborts_barrier_and_reaches_caller(self):
        script = (
            "from unittest import mock\n"
            "import thread_safety\n"
            "patcher = mock.patch.object(thread_safety, 'complicated_calculation', "
            "side_effect=RuntimeError('worker failed'))\n"
            "patcher.start()\n"
            "try:\n"
            "    thread_safety.run_shared_sum([1.0, 2.0], 2, use_lock=False, iterations=2)\n"
            "except RuntimeError as exc:\n"
            "    assert str(exc) == 'worker failed'\n"
            "else:\n"
            "    raise SystemExit(1)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_partial_thread_start_failure_aborts_barrier_and_joins_workers(self):
        script = (
            "import threading\n"
            "from unittest import mock\n"
            "import thread_safety\n"
            "original_start = threading.Thread.start\n"
            "starts = [0]\n"
            "def fail_second_start(thread):\n"
            "    starts[0] += 1\n"
            "    if starts[0] == 2:\n"
            "        raise RuntimeError('cannot start new thread')\n"
            "    return original_start(thread)\n"
            "with mock.patch.object(threading.Thread, 'start', new=fail_second_start):\n"
            "    try:\n"
            "        thread_safety.run_shared_sum([1.0, 2.0], 2, use_lock=False, iterations=2)\n"
            "    except RuntimeError as exc:\n"
            "        assert str(exc) == 'cannot start new thread'\n"
            "    else:\n"
            "        raise SystemExit(1)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_runs_repeated_comparisons_and_prints_sequential_total(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "thread_safety.py"),
                str(ROOT / "zahlen.txt"),
                "--threads",
                "3",
                "--iterations",
                "10",
                "--repeats",
                "2",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("ohne Lock"), 2)
        self.assertEqual(result.stdout.count("mit Lock"), 2)
        self.assertIn("Soll (sequenziell):", result.stdout)

    def test_invalid_iterations_make_cli_exit_nonzero(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "thread_safety.py"),
                str(ROOT / "zahlen.txt"),
                "--threads",
                "3",
                "--iterations",
                "0",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Fehler:", result.stderr)
        self.assertNotIn("Exception in thread", result.stderr)


class ProducerConsumerTests(unittest.TestCase):
    def test_bounded_queue_transfers_all_values_and_terminates(self):
        values = list(range(1, 21))
        received, total = producer_consumer.produce_consume(values, queue_size=2)
        self.assertEqual(received, values)
        self.assertEqual(total, sum(values))

    def test_empty_input_terminates_cleanly(self):
        self.assertEqual(producer_consumer.produce_consume([], queue_size=1), ([], 0))

    def test_nonpositive_queue_size_is_rejected(self):
        with self.assertRaises(ValueError):
            producer_consumer.produce_consume([1], queue_size=0)

    def test_non_integer_queue_values_are_rejected_before_threads_start(self):
        with self.assertRaises(TypeError):
            producer_consumer.produce_consume([1, "2"], queue_size=2)

    def test_partial_thread_start_failure_stops_and_joins_consumer(self):
        script = (
            "import threading\n"
            "from unittest import mock\n"
            "import producer_consumer\n"
            "original_start = threading.Thread.start\n"
            "starts = [0]\n"
            "def fail_second_start(thread):\n"
            "    starts[0] += 1\n"
            "    if starts[0] == 2:\n"
            "        raise RuntimeError('cannot start new thread')\n"
            "    return original_start(thread)\n"
            "with mock.patch.object(threading.Thread, 'start', new=fail_second_start):\n"
            "    try:\n"
            "        producer_consumer.produce_consume([1, 2], queue_size=1)\n"
            "    except RuntimeError as exc:\n"
            "        assert str(exc) == 'cannot start new thread'\n"
            "    else:\n"
            "        raise SystemExit(1)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_queue_access_and_accounting_errors_propagate_without_worker_leaks(self):
        script = (
            "import threading\n"
            "from unittest import mock\n"
            "import producer_consumer\n"
            "queue_type = producer_consumer.queue.Queue\n"
            "for method in ('get', 'task_done'):\n"
            "    with mock.patch.object(queue_type, method, side_effect=RuntimeError(method + ' failed')):\n"
            "        try:\n"
            "            producer_consumer.produce_consume([1, 2, 3], queue_size=1)\n"
            "        except RuntimeError as exc:\n"
            "            assert str(exc) == method + ' failed'\n"
            "        else:\n"
            "            raise SystemExit(1)\n"
            "        assert not any(thread.name in ('producer', 'consumer') for thread in threading.enumerate())\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_consumer_exception_propagates_without_hanging_producer(self):
        script = (
            "import producer_consumer\n"
            "class BadInt(int):\n"
            "    def __radd__(self, other):\n"
            "        raise RuntimeError('consumer failed')\n"
            "try:\n"
            "    producer_consumer.produce_consume([BadInt(1), 2, 3], queue_size=1)\n"
            "except RuntimeError as exc:\n"
            "    assert str(exc) == 'consumer failed'\n"
            "else:\n"
            "    raise SystemExit(1)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
