from dataclasses import dataclass
from signal import SIGKILL
import seppuku
import os


def test_sepukku(monkeypatch):
    counters = [0, 0, 0, 0, 0]

    @dataclass
    class mock_process:
        pid: int

    def mock_kill(pid, signal):
        nonlocal counters
        counters[0] += 1
        assert signal == SIGKILL
        if pid == 1:
            counters[3] += 1
            raise Exception("Dummy")
        if pid == 2:
            counters[4] += 1

    def mock_killpg(pgid, signal):
        nonlocal counters
        counters[1] += 1
        assert signal == SIGKILL
        assert pgid == 42

    def mock_getpgid(pid):
        nonlocal counters
        counters[2] += 1
        assert pid == 0
        return 42

    monkeypatch.setattr(os, "kill", mock_kill)
    monkeypatch.setattr(os, "killpg", mock_killpg)
    monkeypatch.setattr(os, "getpgid", mock_getpgid)
    seppuku.register_process(mock_process(1))
    seppuku.register_process(mock_process(2))
    seppuku.seppuku()
    assert counters == [2, 1, 1, 1, 1]
