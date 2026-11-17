# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Pruefe Blatt-05-Framing unabhaengig mit Fragmenten, mehreren
# Frames pro Empfang, Leerframe, UTF-8, Abbruch und ueberlanger Laenge;
# teste Client und Server auch als echte TCP-Prozesse.
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import threading
import unittest
from framing import MAX_FRAME, recv_exact, recv_frame, send_frame


class FragmentSocket:
    def __init__(self, data, step=1):
        self.data = data
        self.step = step

    def recv(self, size):
        count = min(size, self.step)
        data, self.data = self.data[:count], self.data[count:]
        return data


class FramingTests(unittest.TestCase):
    def test_fragmentation(self):
        for step in (1, 2, 3, 4, 8, 1024):
            with self.subTest(step=step):
                payload = "Grüße aus Klagenfurt".encode()
                sock = FragmentSocket(struct.pack("!I", len(payload)) + payload, step)
                self.assertEqual(recv_frame(sock, 7), payload)
                self.assertIsNone(recv_frame(sock))

    def test_coalesced_and_empty(self):
        sock = FragmentSocket(b"\0\0\0\1A\0\0\0\0\0\0\0\2BC", 100)
        self.assertEqual(recv_frame(sock), b"A")
        self.assertEqual(recv_frame(sock), b"")
        self.assertEqual(recv_frame(sock), b"BC")
        self.assertIsNone(recv_frame(sock))

    def test_truncation(self):
        for data in (b"\0", b"\0\0\0", b"\0\0\0\3ab"):
            with self.subTest(data=data), self.assertRaises(EOFError):
                recv_frame(FragmentSocket(data))

    def test_limit(self):
        with self.assertRaises(ValueError):
            recv_frame(FragmentSocket(struct.pack("!I", MAX_FRAME + 1)))
        with self.assertRaises(ValueError):
            send_frame(None, b"x" * (MAX_FRAME + 1))

    def test_bad_chunk(self):
        with self.assertRaises(ValueError):
            recv_exact(FragmentSocket(b"a"), 1, 0)

    def test_real_socketpair(self):
        a, b = socket.socketpair()
        messages = [b"", bytes(range(256)) * 4096, b"last"]
        errors = []
        def sender():
            try:
                for data in messages:
                    send_frame(a, data)
                a.shutdown(socket.SHUT_WR)
            except Exception as error:
                errors.append(error)
        t = threading.Thread(target=sender)
        t.start()
        try:
            b.settimeout(10)
            for expected in messages:
                self.assertEqual(recv_frame(b, 19), expected)
            self.assertIsNone(recv_frame(b))
        finally:
            a.close()
            b.close()
            t.join(timeout=10)
        self.assertFalse(t.is_alive())
        self.assertEqual(errors, [])

    def test_tcp_processes(self):
        root = Path(__file__).resolve().parent
        for mode in ("framed", "raw"):
            for size in (1, 8, 1024):
                with self.subTest(mode=mode, size=size):
                    # Der freigegebene Port wird direkt danach vom Server belegt.
                    with socket.socket() as probe:
                        probe.bind(("127.0.0.1", 0))
                        port = probe.getsockname()[1]
                    common = ["--host", "127.0.0.1", "--port", str(port), "--mode", mode]
                    server = subprocess.Popen([sys.executable, "-u", str(root / "tcp_server.py"), *common, "--once", "--recv-size", str(size)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    try:
                        self.assertEqual(server.stdout.readline().strip(), "READY")
                        r = subprocess.run([sys.executable, str(root / "tcp_client.py"), *common], capture_output=True, text=True, timeout=15)
                        self.assertEqual(r.returncode, 0, r.stderr)
                        self.assertIn("OK 4 Nachrichten 31 Nutzbytes", r.stdout)
                        stdout, stderr = server.communicate(timeout=15)
                        self.assertEqual(server.returncode, 0, stderr)
                    finally:
                        if server.poll() is None:
                            server.kill()
                            server.communicate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
