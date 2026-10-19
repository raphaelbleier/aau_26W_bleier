"""Ü 3.3: POP3-Laborserver, nur an Loopback betreiben.

KI-Kennzeichnung: Hermes Agent v0.21.5, gpt-6.1-sol, 19.10.2026.
Anfrage: Ü 3.3: Minimalen POP3-Server mit der bereitgestellten SampleDataBase
und einem Thread pro Benutzer implementieren; mit echten Clients testen.
"""
import argparse
import hashlib
import importlib.util
import socketserver
import threading


def canonical(raw):
    text = raw.replace('\r\n', '\n').replace('\r', '\n')
    normalized = text.replace('\n', '\r\n').encode('utf-8')
    return normalized if normalized.endswith(b'\r\n') else normalized + b'\r\n'


class MailStore:
    def __init__(self, db):
        self.db = db
        self.guard = threading.Lock()
        self.locks = {}
        self.deleted = {}

    def lock_for(self, user):
        with self.guard:
            return self.locks.setdefault(user, threading.Lock())

    def messages(self, user):
        removed = self.deleted.get(user, set())
        return [(m['id'], canonical(m['raw'])) for m in self.db.get_messages(user)
                if m['id'] not in removed]

    def commit(self, user, ids):
        # Der Maildrop-Lock schützt auch diesen laufzeitlokalen Löschstand.
        self.deleted.setdefault(user, set()).update(ids)


class POPHandler(socketserver.StreamRequestHandler):
    server: 'POPServer'
    timeout = 600

    def reply(self, text):
        self.wfile.write(text.encode('ascii') + b'\r\n')

    def multi(self, lines):
        for line in lines:
            if line.startswith(b'.'):
                line = b'.' + line
            self.wfile.write(line + b'\r\n')
        self.wfile.write(b'.\r\n')

    def handle(self):
        self.user = None
        self.mail_lock = None
        self.transaction = False
        self.messages = []
        self.removed = set()
        self.reply('+OK POP3 laboratory ready')
        try:
            while True:
                line = self.rfile.readline(513)
                if not line:
                    return
                if len(line) > 512 or not line.endswith(b'\r\n'):
                    self.reply('-ERR invalid command line')
                    return
                try:
                    words = line[:-2].decode('ascii').split(' ', 1)
                except UnicodeDecodeError:
                    self.reply('-ERR ASCII commands required')
                    continue
                command = words[0].upper()
                arg = words[1] if len(words) == 2 else ''
                if command == 'QUIT' and not arg:
                    if self.transaction:
                        self.server.store.commit(self.user, {
                            self.messages[i - 1][0] for i in self.removed})
                    self.reply('+OK goodbye')
                    return
                if command == 'CAPA' and not arg:
                    self.reply('+OK capability list follows')
                    self.multi([b'USER', b'UIDL', b'TOP', b'IMPLEMENTATION lab-pop3'])
                elif not self.transaction:
                    self.authorize(command, arg)
                else:
                    self.transact(command, arg)
        except (OSError, ValueError):
            return
        finally:
            if self.mail_lock is not None:
                self.mail_lock.release()

    def authorize(self, command, arg):
        if command == 'USER' and arg and ' ' not in arg:
            self.user = arg
            self.reply('+OK send password')
        elif command == 'PASS' and self.user is not None and arg:
            if not self.server.store.db.authenticate(self.user, arg):
                self.user = None
                self.reply('-ERR authentication failed')
                return
            lock = self.server.store.lock_for(self.user)
            if not lock.acquire(blocking=False):
                self.reply('-ERR maildrop locked')
                return
            self.mail_lock = lock
            self.messages = self.server.store.messages(self.user)
            self.transaction = True
            self.reply('+OK maildrop locked and ready')
        else:
            self.reply('-ERR USER and PASS required')

    def available(self):
        return [(i, ident, raw) for i, (ident, raw) in enumerate(self.messages, 1)
                if i not in self.removed]

    def get_number(self, arg):
        if not arg.isascii() or not arg.isdigit():
            raise ValueError('number required')
        number = int(arg)
        if number < 1 or number > len(self.messages) or number in self.removed:
            raise ValueError('no such message')
        return number

    def uid(self, ident, raw):
        # Die ursprüngliche DB-ID verhindert Kollisionen bei identischen Mails.
        return hashlib.sha256(str(ident).encode('ascii') + b':' + raw).hexdigest().encode('ascii')

    def transact(self, command, arg):
        try:
            if command == 'STAT' and not arg:
                mails = self.available()
                self.reply('+OK %d %d' % (len(mails), sum(len(m[2]) for m in mails)))
            elif command in ('LIST', 'UIDL'):
                if arg:
                    n = self.get_number(arg)
                    ident, raw = self.messages[n - 1]
                    value = str(len(raw)).encode() if command == 'LIST' else self.uid(ident, raw)
                    self.reply('+OK %d %s' % (n, value.decode('ascii')))
                else:
                    self.reply('+OK listing follows')
                    self.multi([str(n).encode() + b' ' +
                                (str(len(raw)).encode() if command == 'LIST' else self.uid(ident, raw))
                                for n, ident, raw in self.available()])
            elif command == 'RETR':
                n = self.get_number(arg)
                raw = self.messages[n - 1][1]
                self.reply('+OK %d octets' % len(raw))
                self.multi(raw[:-2].split(b'\r\n'))
            elif command == 'TOP':
                args = arg.split()
                if len(args) != 2 or not args[1].isascii() or not args[1].isdigit():
                    raise ValueError('TOP needs message and line count')
                n = self.get_number(args[0])
                head, sep, body = self.messages[n - 1][1].partition(b'\r\n\r\n')
                lines = head.split(b'\r\n') + [b'']
                if sep:
                    lines += body[:-2].split(b'\r\n')[:int(args[1])]
                self.reply('+OK top follows')
                self.multi(lines)
            elif command == 'DELE':
                self.removed.add(self.get_number(arg))
                self.reply('+OK marked for deletion')
            elif command == 'RSET' and not arg:
                self.removed.clear()
                self.reply('+OK deletion marks cleared')
            elif command == 'NOOP' and not arg:
                self.reply('+OK')
            else:
                self.reply('-ERR unsupported command or arguments')
        except ValueError:
            self.reply('-ERR invalid message or arguments')


class POPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, db):
        self.store = MailStore(db)
        super().__init__(address, POPHandler)


def load_database(path):
    spec = importlib.util.spec_from_file_location('course_database', path)
    if spec is None or spec.loader is None:
        raise ValueError('Datenbankmodul kann nicht geladen werden')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SampleDataBase()


def main():
    parser = argparse.ArgumentParser(description='POP3-Laborserver ohne TLS')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=11110)
    parser.add_argument('--database', required=True, help='Original SampleDataBase.py aus Moodle')
    args = parser.parse_args()
    with POPServer((args.host, args.port), load_database(args.database)) as server:
        print('POP3-Laborserver gestartet', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
