"""Socket-Integrationstests mit eigenen Testdaten.

KI-Kennzeichnung: Hermes Agent v0.21.5, gpt-6.1-sol, 19.10.2026.
Anfrage: Ü 3.2–3.5 gegen unabhängige Standardbibliotheks-Clients prüfen,
Fehler, Framing, Parallelität und Pfadgrenzen testen.
"""
from contextlib import contextmanager
import concurrent.futures
import http.client
import io
from pathlib import Path
import poplib
import socket
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pop3_client import POPClient, POPError
from pop3_server import POPServer, canonical
from http_server import (BatchLogger, HTTPServer, HTTP09Handler,
                         HTTP10Handler, ThreadedHTTPServer, target_file)


class Database:
    def authenticate(self, user, password):
        return user in ('reader', 'other') and password == 'test-only'

    def get_messages(self, user):
        return [{'id': 17, 'raw': 'From: test@example.invalid\r\nSubject: Test\r\n\r\n.first\r\n.\r\nlast\r\n\r\n'},
                {'id': 29, 'raw': 'Subject: Second\n\nGrüße\n'}]


@contextmanager
def running(server):
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01})
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)
        assert not thread.is_alive()


class POPTests(unittest.TestCase):
    def setUp(self):
        self.server = POPServer(('127.0.0.1', 0), Database())
        self.context = running(self.server)
        self.host, self.port = self.context.__enter__()

    def tearDown(self):
        self.context.__exit__(None, None, None)

    def client(self, user='reader'):
        c = poplib.POP3(self.host, self.port, timeout=2)
        c.user(user)
        c.pass_('test-only')
        self.addCleanup(c.close)
        return c

    def test_own_client_lists_retrieves_and_quits(self):
        with POPClient(self.host, self.port) as c:
            c.login('reader', 'test-only')
            self.assertEqual(c.list(), [(i, len(canonical(m['raw']))) for i, m in enumerate(Database().get_messages('reader'), 1)])
            self.assertEqual(c.retrieve(1), canonical(Database().get_messages('reader')[0]['raw']))
        self.assertTrue(c.closed)

    def test_poplib_dot_unstuff_and_byte_counts(self):
        c = self.client()
        status, lines, octets = c.retr(1)
        raw = b'\r\n'.join(lines) + b'\r\n'
        self.assertEqual(raw, canonical(Database().get_messages('reader')[0]['raw']))
        self.assertIn(b'.first', lines)
        self.assertIn(b'.', lines)
        self.assertEqual(c.stat(), (2, sum(len(canonical(m['raw'])) for m in Database().get_messages('reader'))))
        c.quit()

    def test_bad_password_and_transaction_before_login(self):
        c = poplib.POP3(self.host, self.port, timeout=2)
        self.addCleanup(c.close)
        with self.assertRaises(poplib.error_proto):
            c.stat()
        c.user('reader')
        with self.assertRaises(poplib.error_proto):
            c.pass_('wrong')
        c.quit()

    def test_capa_top_uidl(self):
        c = self.client()
        self.assertIn('USER', c.capa())
        self.assertEqual(c.top(1, 0)[1], [b'From: test@example.invalid', b'Subject: Test', b''])
        ids = c.uidl()[1]
        self.assertEqual(len(ids), 2)
        self.assertNotEqual(ids[0].split()[1], ids[1].split()[1])
        self.assertEqual(c.uidl(1).split()[2], ids[0].split()[1])
        self.assertEqual(c.list(1).split()[2], str(len(canonical(Database().get_messages('reader')[0]['raw']))).encode())
        c.noop()
        c.quit()

    def test_same_maildrop_locked_other_user_allowed(self):
        c = self.client()
        other = self.client('other')
        self.assertEqual(other.stat()[0], 2)
        duplicate = poplib.POP3(self.host, self.port, timeout=2)
        self.addCleanup(duplicate.close)
        duplicate.user('reader')
        with self.assertRaises(poplib.error_proto):
            duplicate.pass_('test-only')
        duplicate.quit()
        other.quit()
        c.quit()

    def test_dele_rset_and_quit_commit(self):
        c = self.client()
        c.dele(1)
        self.assertEqual(c.stat()[0], 1)
        with self.assertRaises(poplib.error_proto):
            c.retr(1)
        c.rset()
        self.assertEqual(c.stat()[0], 2)
        c.dele(1)
        c.quit()
        d = self.client()
        self.assertEqual(d.stat()[0], 1)
        self.assertEqual(d.retr(1)[1][0], b'Subject: Second')
        d.quit()

    def test_disconnect_rolls_back(self):
        c = self.client()
        c.dele(1)
        c.close()
        # Zweiter Benutzer bestätigt nebenbei, dass der Server noch arbeitet.
        d = self.client('other')
        d.quit()
        self.assertEqual(len(self.server.store.messages('reader')), 2)

    def test_command_injection_rejected(self):
        with POPClient(self.host, self.port) as c:
            with self.assertRaises(ValueError):
                c.command('USER reader\r\nQUIT')

    def test_invalid_message_numbers(self):
        c = self.client()
        for n in [0, -1, 3]:
            with self.assertRaises(poplib.error_proto):
                c.retr(n)
        c.quit()

    def test_canonical_preserves_blank_lines(self):
        self.assertEqual(canonical('a\n\n'), b'a\r\n\r\n')

    def test_parallel_users(self):
        def read(user):
            with POPClient(self.host, self.port) as c:
                c.login(user, 'test-only')
                return c.retrieve(2)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            data = list(pool.map(read, ['reader', 'other']))
        self.assertEqual(data[0], data[1])

    def test_fragmented_reply_and_eof(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            def peer():
                with listener.accept()[0] as conn:
                    for part in [b'+', b'OK\r', b'\n']:
                        conn.sendall(part)
                    conn.recv(1024)
                    conn.sendall(b'+OK\r\n..point\r\n.\r\n')
                    conn.recv(1024)
            t = threading.Thread(target=peer)
            t.start()
            c = POPClient(*listener.getsockname())
            try:
                self.assertEqual(c.command('LIST', True), [b'.point'])
                with self.assertRaises(POPError):
                    c.command('QUIT')
            finally:
                c.close()
                t.join(2)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'index.html').write_bytes(b'<html>lab</html>')
        (self.root/'binary.bin').write_bytes(bytes(range(256)))
        (self.root/'sub').mkdir()
        (self.root/'sub/index.html').write_bytes(b'subdirectory')

    def raw(self, address, data):
        with socket.create_connection(address, timeout=2) as s:
            s.sendall(data)
            s.shutdown(socket.SHUT_WR)
            result = bytearray()
            while True:
                block = s.recv(65536)
                if not block:
                    return bytes(result)
                result.extend(block)

    @contextmanager
    def modern(self):
        logger = BatchLogger(io.StringIO(), .02)
        try:
            with running(ThreadedHTTPServer(('127.0.0.1', 0), self.root, HTTP10Handler, logger)) as address:
                yield address
        finally:
            logger.close()

    def test_http09_index_binary_and_subdirectory(self):
        with running(HTTPServer(('127.0.0.1', 0), self.root)) as a:
            self.assertEqual(self.raw(a, b'GET /\r\n'), b'<html>lab</html>')
            self.assertEqual(self.raw(a, b'GET /binary.bin\r\n'), bytes(range(256)))
            self.assertEqual(self.raw(a, b'GET /sub/\r\n'), b'subdirectory')

    def test_http09_errors_have_no_response(self):
        with running(HTTPServer(('127.0.0.1', 0), self.root)) as a:
            for request in [b'GET /missing\r\n', b'GET /../x\r\n', b'POST /\r\n', b'GET / HTTP/1.1\r\n', b'GET /\n']:
                self.assertEqual(self.raw(a, request), b'')

    def test_paths_and_symlinks_cannot_escape(self):
        for target in ['/../x', '/%2e%2e/x', '/%00', '/a\\b', 'http://example.invalid/x', '//example.invalid/x']:
            with self.assertRaises((ValueError, FileNotFoundError)):
                target_file(self.root, target)
        (self.root/'escape').symlink_to(self.root.parent)
        with self.assertRaises(ValueError):
            target_file(self.root, '/escape/file')
        (self.root/'sub/index.html').unlink()
        (self.root/'sub/index.html').symlink_to(self.root.parent/'outside')
        with self.assertRaises(ValueError):
            target_file(self.root, '/sub/')

    def test_http10_httpclient_headers_and_head(self):
        with self.modern() as a:
            c = http.client.HTTPConnection(*a, timeout=2)
            self.addCleanup(c.close)
            c.request('GET', '/')
            r = c.getresponse()
            self.assertEqual(r.version, 10)
            self.assertEqual(r.status, 200)
            self.assertEqual(r.getheader('Content-Length'), '16')
            self.assertEqual(r.read(), b'<html>lab</html>')
            c.request('HEAD', '/binary.bin')
            r = c.getresponse()
            self.assertEqual(r.getheader('Content-Length'), '256')
            self.assertEqual(r.read(), b'')

    def test_two_requests_one_connection_and_pipeline(self):
        with self.modern() as a:
            data = self.raw(a, b'GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\nGET /binary.bin HTTP/1.0\r\n\r\n')
            self.assertEqual(data.count(b'HTTP/1.0 200 OK'), 2)
            self.assertIn(b'Connection: keep-alive', data)
            self.assertTrue(data.endswith(bytes(range(256))))

    def test_http10_errors_and_body_rejection(self):
        with self.modern() as a:
            pairs = [(b'GET /missing HTTP/1.0\r\n\r\n', b'404'),
                     (b'GET /../x HTTP/1.0\r\n\r\n', b'403'),
                     (b'POST / HTTP/1.0\r\n\r\n', b'405'),
                     (b'GET / HTTP/1.0\r\nContent-Length: 1\r\n\r\nx', b'400'),
                     (b'GET / HTTP/1.0\r\nTransfer-Encoding: chunked\r\n\r\n', b'400'),
                     (b'GET / HTTP/1.0\r\nX: a\r\nX: b\r\n\r\n', b'400'),
                     (b'GET / HTTP/1.0\r\nBad header: a\r\n\r\n', b'400')]
            for request, code in pairs:
                self.assertTrue(self.raw(a, request).startswith(b'HTTP/1.0 ' + code))

    def test_parallel_requests(self):
        with self.modern() as a:
            with concurrent.futures.ThreadPoolExecutor(8) as pool:
                answers = list(pool.map(lambda _: self.raw(a, b'GET / HTTP/1.0\r\n\r\n'), range(16)))
            self.assertTrue(all(x.endswith(b'<html>lab</html>') for x in answers))

    def test_logger_batches_and_flushes_on_close(self):
        output = io.StringIO()
        logger = BatchLogger(output, 5)
        logger.record('GET', ('127.0.0.1', 23456))
        self.assertEqual(output.getvalue(), '')
        logger.close()
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn('GET 127.0.0.1 23456', lines[0])

    def test_logger_periodic_flush(self):
        event = threading.Event()
        class Stream(io.StringIO):
            def flush(self):
                event.set()
        stream = Stream()
        logger = BatchLogger(stream, .05)
        try:
            logger.record('HEAD', ('127.0.0.1', 12345))
            self.assertTrue(event.wait(1))
            self.assertIn('HEAD', stream.getvalue())
        finally:
            logger.close()


if __name__ == '__main__':
    unittest.main()
