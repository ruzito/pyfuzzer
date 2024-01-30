import signal
import os

_pids = set()


def register_process(process):
    global _pids
    _pids.add(process.pid)


def release_process(process):
    global _pids
    _pids.remove(process.pid)


def seppuku():
    global _pids
    for pid in _pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except BaseException:
            pass

    os.killpg(os.getpgid(0), signal.SIGKILL)
