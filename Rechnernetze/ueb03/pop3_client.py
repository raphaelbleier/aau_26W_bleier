"""Ü 3.2: POP3 über Sockets, ohne poplib.

KI-Kennzeichnung: Hermes Agent v0.21.5, gpt-6.1-sol, 19.10.2026.
Anfrage: Ü 3.2: Socket-Client anmelden, Nachrichten auflisten und abrufen;
Standardbibliothek verwenden und die Verbindung ordentlich beenden.
"""
import argparse
import getpass
import socket


class POPError(Exception):
    pass


class POPClient:
    def __init__(self, host, port=110, timeout=10):
        self.sock = socket.create_connection((host, port), timeout)
        self.reader = self.sock.makefile('rb')
        self.closed = False
        try:
            self._status()
        except BaseException:
            self.close()
            raise

    def _line(self):
        line = self.reader.readline(65537)
        if not line.endswith(b'\r\n') or len(line) > 65536:
            raise POPError('Ungültige oder zu lange Antwort')
        return line[:-2]

    def _status(self):
        line = self._line()
        if line != b'+OK' and not line.startswith(b'+OK '):
            raise POPError(line.decode('utf-8', errors='replace'))
        return line

    def command(self, command, multiline=False):
        if '\r' in command or '\n' in command:
            raise ValueError('Zeilenumbruch im Kommando')
        self.sock.sendall(command.encode('ascii') + b'\r\n')
        status = self._status()
        if not multiline:
            return status
        lines = []
        size = 0
        while True:
            line = self._line()
            if line == b'.':
                return lines
            if line.startswith(b'..'):
                line = line[1:]
            size += len(line) + 2
            if size > 20 * 1024 * 1024:
                raise POPError('Antwort größer als 20 MiB')
            lines.append(line)

    def login(self, user, password):
        self.command('USER ' + user)
        self.command('PASS ' + password)

    def list(self):
        return [tuple(map(int, line.split())) for line in self.command('LIST', True)]

    def retrieve(self, number):
        if not isinstance(number, int) or number <= 0:
            raise ValueError('Nachrichtennummer muss positiv sein')
        return b'\r\n'.join(self.command('RETR ' + str(number), True)) + b'\r\n'

    def quit(self):
        try:
            if not self.closed:
                self.command('QUIT')
        finally:
            self.close()

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.reader.close()
            finally:
                self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if exc[0] is None:
            self.quit()
        else:
            self.close()


def main():
    parser = argparse.ArgumentParser(description='POP3-Labortest ohne TLS, nur lokal verwenden')
    parser.add_argument('host')
    parser.add_argument('--port', type=int, default=110)
    parser.add_argument('--user', required=True)
    parser.add_argument('--message', type=int, default=1)
    args = parser.parse_args()
    try:
        with POPClient(args.host, args.port) as client:
            client.login(args.user, getpass.getpass())
            print('Nummer / Bytes:', client.list())
            print(client.retrieve(args.message).decode('utf-8', errors='replace'))
    except (OSError, POPError, ValueError, UnicodeError) as exc:
        parser.exit(1, 'POP3-Fehler: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
