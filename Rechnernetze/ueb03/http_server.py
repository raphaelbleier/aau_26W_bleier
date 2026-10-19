"""Ü 3.4/3.5: HTTP/0.9 und HTTP/1.0, ohne http.server.

KI-Kennzeichnung: Hermes Agent v0.21.5, gpt-6.1-sol, 19.10.2026.
Anfrage: Ü 3.4/3.5: Single-Thread-HTTP/0.9 mit document root und index.html;
Multi-Thread-HTTP/1.0, persistente Verbindungen und separater Logger alle 5 s.
"""
import argparse
from datetime import datetime, timezone
import mimetypes
from pathlib import Path
import queue
import socketserver
import sys
import threading
import time
from urllib.parse import unquote, urlsplit


class BatchLogger:
    def __init__(self, stream=None, interval: float = 5):
        self.queue = queue.Queue()
        self.stream = stream if stream is not None else sys.stdout
        self.interval = interval
        self.thread = threading.Thread(target=self.run, name='access-logger')
        self.thread.start()

    def record(self, method, peer):
        # Kein Request-Pfad und keine Header: keine Zugangsdaten im Zugriffslog.
        self.queue.put((datetime.now(timezone.utc).isoformat(), method, peer[0], peer[1]))

    def run(self):
        pending = []
        deadline = time.monotonic() + self.interval
        while True:
            try:
                record = self.queue.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                record = False
            if record is not False and record is not None:
                pending.append(record)
            if record is None or time.monotonic() >= deadline:
                if pending:
                    self.stream.write(''.join('%s %s %s %s\n' % row for row in pending))
                    self.stream.flush()
                    pending.clear()
                deadline = time.monotonic() + self.interval
            if record is None:
                return

    def close(self):
        self.queue.put(None)
        self.thread.join()


def target_file(root, target):
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or parts.fragment or not target.startswith('/'):
        raise ValueError('origin-form required')
    decoded = unquote(parts.path, errors='strict')
    if '\x00' in decoded or '\\' in decoded or '..' in decoded.split('/'):
        raise ValueError('invalid path')
    path = (root / decoded.lstrip('/')).resolve()
    if path != root and root not in path.parents:
        raise ValueError('outside document root')
    if path.is_dir():
        path = (path / 'index.html').resolve()
        if path != root and root not in path.parents:
            raise ValueError('index outside document root')
    if not path.is_file():
        raise FileNotFoundError('not a regular file')
    return path


def response(root, method, target):
    if method not in ('GET', 'HEAD'):
        return '405 Method Not Allowed', b'Method not allowed\n', 'text/plain; charset=utf-8'
    try:
        path = target_file(root, target)
        body = path.read_bytes()
        mime = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        return '200 OK', body, mime
    except FileNotFoundError:
        return '404 Not Found', b'Not found\n', 'text/plain; charset=utf-8'
    except (ValueError, UnicodeError, OSError):
        return '403 Forbidden', b'Forbidden\n', 'text/plain; charset=utf-8'


class HTTP09Handler(socketserver.StreamRequestHandler):
    server: 'HTTPServer'
    timeout = 5

    def handle(self):
        try:
            line = self.rfile.readline(8193)
            if len(line) > 8192 or not line.endswith(b'\r\n'):
                return
            words = line[:-2].decode('ascii').split()
            if len(words) != 2 or words[0] != 'GET':
                return
            path = target_file(self.server.root, words[1])
            with path.open('rb') as file:
                while True:
                    block = file.read(65536)
                    if not block:
                        return
                    self.wfile.write(block)
        except (OSError, UnicodeError, ValueError):
            return


class HTTP10Handler(socketserver.StreamRequestHandler):
    server: 'HTTPServer'
    timeout = 5

    def handle(self):
        try:
            for _ in range(100):
                request = self.read_request()
                if request is None:
                    return
                method, target, keep = request
                self.server.logger.record(method, self.client_address)
                # Jede Anfrage erhält einen eigenen Worker. Auf derselben Verbindung
                # warten wir vor dem nächsten Request auf die vollständige Antwort.
                result = []

                def work():
                    result.append(response(self.server.root, method, target))

                worker = threading.Thread(target=work, name='http-request')
                worker.start()
                worker.join()
                if not result:
                    self.error('500 Internal Server Error')
                    return
                status, body, mime = result[0]
                headers = ('HTTP/1.0 ' + status + '\r\nContent-Length: ' + str(len(body)) +
                           '\r\nContent-Type: ' + mime + '\r\nConnection: ' +
                           ('keep-alive' if keep and _ < 99 else 'close') + '\r\n')
                if status.startswith('405'):
                    headers += 'Allow: GET, HEAD\r\n'
                self.wfile.write(headers.encode('ascii') + b'\r\n')
                if method != 'HEAD':
                    self.wfile.write(body)
                if not keep:
                    return
        except (OSError, UnicodeError, ValueError):
            return

    def error(self, status):
        self.wfile.write(('HTTP/1.0 ' + status +
                          '\r\nContent-Length: 0\r\nConnection: close\r\n\r\n').encode('ascii'))

    def read_request(self):
        line = self.rfile.readline(8193)
        if not line:
            return None
        if len(line) > 8192 or not line.endswith(b'\r\n'):
            self.error('400 Bad Request')
            return None
        words = line[:-2].decode('ascii').split()
        if len(words) != 3 or words[2] not in ('HTTP/1.0', 'HTTP/1.1'):
            self.error('400 Bad Request')
            return None
        method, target, version = words
        headers = {}
        size = len(line)
        while True:
            line = self.rfile.readline(8193)
            size += len(line)
            if size > 32768 or len(line) > 8192 or not line.endswith(b'\r\n'):
                self.error('400 Bad Request')
                return None
            if line == b'\r\n':
                break
            name, sep, value = line[:-2].partition(b':')
            token = b"!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            if not sep or not name or any(c not in token for c in name):
                self.error('400 Bad Request')
                return None
            key = name.decode('ascii').lower()
            if key in headers:
                self.error('400 Bad Request')
                return None
            headers[key] = value.strip().decode('ascii')
        if 'transfer-encoding' in headers or headers.get('content-length', '0') != '0':
            self.error('400 Bad Request')
            return None
        options = {x.strip().lower() for x in headers.get('connection', '').split(',')}
        keep = 'keep-alive' in options and 'close' not in options
        return method, target, keep


class HTTPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, address, root, handler: type[socketserver.BaseRequestHandler] = HTTP09Handler, logger=None):
        self.root = Path(root).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError('document root must be a directory')
        self.logger = logger
        super().__init__(address, handler)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description='HTTP-Laborserver')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--root', required=True)
    parser.add_argument('--mode', choices=['09', '10'], default='09')
    args = parser.parse_args()
    logger = BatchLogger() if args.mode == '10' else None
    cls = ThreadedHTTPServer if args.mode == '10' else HTTPServer
    handler = HTTP10Handler if args.mode == '10' else HTTP09Handler
    try:
        with cls((args.host, args.port), args.root, handler, logger) as server:
            print('HTTP-Laborserver gestartet', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    finally:
        if logger:
            logger.close()


if __name__ == '__main__':
    main()
