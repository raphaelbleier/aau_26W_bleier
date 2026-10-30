"""Lokale Gegenprobe für Ü 4.6, ohne Mininet."""
import socket
import threading
import unittest

from tcp_server import handle_lines, handle_single


def free_port():
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


class TcpTests(unittest.TestCase):
    def test_one_message_then_close(self):
        port = free_port()
        seen = []

        def run():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", port))
            server.listen(1)
            server.settimeout(3)
            conn, _ = server.accept()
            try:
                handle_single(conn)
            finally:
                conn.close()
                server.close()

        thread = threading.Thread(target=run)
        thread.start()
        client = socket.create_connection(("127.0.0.1", port), timeout=3)
        client.sendall(b"eine Nachricht")
        client.shutdown(socket.SHUT_WR)
        reply = client.recv(4096)
        client.close()
        thread.join(3)
        self.assertEqual(reply, b"ACK: eine Nachricht")

    def test_several_lines_one_connection(self):
        port = free_port()

        def run():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", port))
            server.listen(1)
            server.settimeout(3)
            conn, _ = server.accept()
            try:
                handle_lines(conn)
            finally:
                conn.close()
                server.close()

        thread = threading.Thread(target=run)
        thread.start()
        client = socket.create_connection(("127.0.0.1", port), timeout=3)
        replies = []
        for text in (b"eins\n", b"zwei\n", b"drei\n", b"QUIT\n"):
            client.sendall(text)
            replies.append(client.recv(4096))
        client.close()
        thread.join(3)
        self.assertEqual(replies[0], b"ACK: eins\n")
        self.assertEqual(replies[1], b"ACK: zwei\n")
        self.assertEqual(replies[2], b"ACK: drei\n")
        self.assertEqual(replies[3], b"BYE\n")

    def test_one_recv_can_hold_two_sends(self):
        port = free_port()
        got = []

        def run():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", port))
            server.listen(1)
            server.settimeout(3)
            conn, _ = server.accept()
            try:
                conn.settimeout(2)
                got.append(conn.recv(4096))
            finally:
                conn.close()
                server.close()

        thread = threading.Thread(target=run)
        thread.start()
        client = socket.create_connection(("127.0.0.1", port), timeout=3)
        # Ein sendall, zwei logische Nachrichten. TCP garantiert die Grenze nicht.
        client.sendall(b"alpha\nbeta\n")
        client.close()
        thread.join(3)
        self.assertEqual(got, [b"alpha\nbeta\n"])


if __name__ == "__main__":
    unittest.main()
