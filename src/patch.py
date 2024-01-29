import asyncio


def new_pipe_connection_lost(self, fd, exc):
    if fd == 0:
        pipe = self.stdin
        if pipe is not None:
            pipe.close()
        self.connection_lost(exc)
        if exc is None:
            self._stdin_closed.set_result(None)
        else:
            self._stdin_closed.set_exception(exc)
            # Since calling `wait_closed()` is not mandatory,
            # we shouldn't log the traceback if this is not awaited.
            self._stdin_closed._log_traceback = False
        return
    if fd == 1:
        reader = self.stdout
    elif fd == 2:
        reader = self.stderr
    else:
        reader = None
    if reader is not None:
        if exc is None:
            reader.feed_eof()
        else:
            reader.set_exception(exc)
    if fd in self._pipe_fds:
        self._pipe_fds.remove(fd)
    self._maybe_close_transport()


# Patch python lib
# See: https://github.com/python/cpython/issues/104340
# It still hasn't been updated in ubuntu repositories
# even tho it was supposed to be part of Python 3.11


def patch():
    asyncio.subprocess.SubprocessStreamProtocol.pipe_connection_lost = (
        new_pipe_connection_lost
    )
