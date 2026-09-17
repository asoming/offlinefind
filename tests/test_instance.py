import json
import multiprocessing
import socket
import subprocess
import sys
import threading

from shiwen.instance import Instance


def child_owner(directory, ready):
    owner = Instance(directory)
    assert owner.acquire()
    owner.listen()
    ready.set()
    threading.Event().wait(60)


def test_same_index_has_one_owner_and_supports_queued_activation(tmp_path):
    owner, other = Instance(tmp_path), Instance(tmp_path)
    try:
        assert owner.acquire()
        owner.listen()
        assert not other.acquire()
        assert other.notify()
        activated = threading.Event()
        owner.set_callback(activated.set)
        assert activated.wait(2)
        activated.clear()
        assert other.notify()
        assert activated.wait(2)
    finally:
        owner.close()
        other.close()
    replacement = Instance(tmp_path)
    try:
        assert replacement.acquire()
    finally:
        replacement.close()


def test_crashed_process_does_not_leave_a_stale_lock(tmp_path):
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    child = context.Process(target=child_owner, args=(tmp_path, ready))
    child.start()
    try:
        assert ready.wait(15)
        contender = Instance(tmp_path)
        assert not contender.acquire()
    finally:
        child.terminate()
        child.join(5)
        if child.is_alive():
            child.kill()
            child.join(5)
    replacement = Instance(tmp_path)
    try:
        assert replacement.acquire()
        replacement.listen()
    finally:
        replacement.close()


def test_activation_rejects_wrong_token_and_separate_indexes_can_run(tmp_path):
    one, two = Instance(tmp_path / "one"), Instance(tmp_path / "two")
    try:
        assert one.acquire() and two.acquire()
        one.listen()
        activated = threading.Event()
        one.set_callback(activated.set)
        with one.path.open("rb") as file:
            file.seek(1)
            record = json.load(file)
        with socket.create_connection(("127.0.0.1", record["port"]), timeout=2) as client:
            client.sendall(b"wrong-token\n")
            assert client.recv(3) == b""
        assert not activated.is_set()
    finally:
        one.close()
        two.close()


def test_cli_reopening_activates_without_opening_another_index(tmp_path):
    owner = Instance(tmp_path)
    activated = threading.Event()
    try:
        assert owner.acquire()
        owner.listen()
        owner.set_callback(activated.set)
        result = subprocess.run(
            [sys.executable, "-m", "shiwen.app", "--data-dir", str(tmp_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        assert result.returncode == 0, result.stderr
        assert "already running" in result.stdout
        assert activated.wait(2)
        assert not list(tmp_path.glob("*.sqlite*"))
    finally:
        owner.close()
