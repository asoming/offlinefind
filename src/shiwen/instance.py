"""One index owner per data directory, with authenticated loopback activation."""

import errno
import json
import logging
import os
import secrets
import socket
import threading
import time
from pathlib import Path


class Instance:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = directory / "instance.lock"
        self.file = None
        self.listener = None
        self.thread = None
        self.stopped = threading.Event()
        self.requested = threading.Event()
        self.callback = None

    def acquire(self):
        self.file = self.path.open("a+b")
        self.path.chmod(0o600)
        if self.path.stat().st_size == 0:
            self.file.write(b" ")
            self.file.flush()
        self.file.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.file.close()
            self.file = None
            if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                raise
            return False
        return True

    def listen(self):
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(4)
        self.listener.settimeout(0.2)
        self.token = secrets.token_hex(32)
        record = {"port": self.listener.getsockname()[1], "token": self.token}
        # Byte zero is reserved for the Windows lock; readers use bytes after it.
        self.file.seek(1)
        self.file.truncate()
        self.file.write(json.dumps(record).encode())
        self.file.flush()
        self.thread = threading.Thread(target=self._listen, name="shiwen-activate", daemon=True)
        self.thread.start()

    def _listen(self):
        while not self.stopped.is_set():
            try:
                connection, _ = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            with connection:
                connection.settimeout(1)
                try:
                    message = b""
                    while len(message) < 128 and not message.endswith(b"\n"):
                        chunk = connection.recv(128 - len(message))
                        if not chunk:
                            break
                        message += chunk
                    if not secrets.compare_digest(message, self.token.encode() + b"\n"):
                        continue
                    self.requested.set()
                    connection.sendall(b"ok\n")
                    self._activate()
                except OSError:
                    continue

    def set_callback(self, callback):
        self.callback = callback
        self._activate()

    def _activate(self):
        if self.callback and self.requested.is_set() and not self.stopped.is_set():
            self.requested.clear()
            try:
                self.callback()
            except Exception:
                logging.getLogger(__name__).exception("Could not activate the existing window")

    def notify(self):
        # A second process can arrive between lock acquisition and listener setup.
        for _ in range(10):
            try:
                with self.path.open("rb") as file:
                    file.seek(1)
                    record = json.loads(file.read(4096))
                port, token = record["port"], record["token"]
                if (
                    not isinstance(port, int)
                    or not 0 < port < 65536
                    or not isinstance(token, str)
                    or len(token) != 64
                ):
                    return False
                with socket.create_connection(("127.0.0.1", port), timeout=0.5) as connection:
                    connection.sendall(token.encode() + b"\n")
                    return connection.recv(3) == b"ok\n"
            except (OSError, ValueError, KeyError, TypeError):
                time.sleep(0.1)
        return False

    def close(self):
        self.stopped.set()
        if self.listener:
            self.listener.close()
        if self.thread:
            self.thread.join(timeout=2)
        if self.file:
            # Do not unlink: another process must lock the same inode after exit.
            if os.name == "nt":
                import msvcrt

                self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            self.file.close()
            self.file = None
