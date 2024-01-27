import asyncio
import psutil
import os
import signal
from typing import List, Tuple

class Runner:
    def __init__(self, cmd, *, timeout:int|float=5000):
        # Define the command and arguments you want to run
        self.command_pattern = cmd
        self.timeout = timeout
        self.chunk_sizes = 1024

    async def run(
        self, input, args
    ) -> Tuple[int | None, bytes | str, bytes | str, bool]:
        if isinstance(input, str):
            byte_input = input.encode("utf-8")
        elif isinstance(input, bytes):
            byte_input = input
        else:
            raise TypeError("Input must be a string or bytes")

        command = ["-c", self.command_pattern.format(**args)]

        # Run the subprocess with input
        process = await asyncio.create_subprocess_exec(
            "bash",
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True
        )

        try:
            if process.stdin is not None:
                process.stdin.write(byte_input)
                await process.stdin.drain()
                process.stdin.close()
        except Exception as e:
            import traceback
            print("Runner caught exception during attempt to write to stdin:\n{}".format(traceback.format_exc()))
            pass

        async def read_stream(stream, chunks, chunk_sizes=1024):
            while True:
                chunk = await stream.read(chunk_sizes)
                if not chunk:
                    break
                chunks.append(chunk)
                if stream.at_eof():
                    return

        # The following shannanigans are here to cope with the fact
        # that I want to be able to get stdout and stderr (at least partialy)
        # even if the cmd times out
        # And be able to have this as an async job that I can stuff into thread pool
        stdout_chunks: List[bytes] = []
        stderr_chunks: List[bytes] = []
        stdout_task = asyncio.create_task(
            read_stream(process.stdout, stdout_chunks, self.chunk_sizes)
        )
        stderr_task = asyncio.create_task(
            read_stream(process.stderr, stderr_chunks, self.chunk_sizes)
        )

        flags = {"cb_run": False, "timed_out": False}

        def kill_proc_tree(pid, including_parent=True):
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            if including_parent:
                parent.kill()
                parent.wait(5)

        def timeout_callback():
            flags["cb_run"] = True
            if stdout_task.done() and stderr_task.done():
                return
            flags["timed_out"] = True
            stdout_task.cancel()
            stderr_task.cancel()

        loop = asyncio.get_event_loop()
        timeout_task = loop.call_later(self.timeout, timeout_callback)

        done, pending = await asyncio.wait(
            [stdout_task, stderr_task], return_when=asyncio.ALL_COMPLETED
        )

        if not flags["cb_run"]:
            timeout_task.cancel()

        if flags["timed_out"]:
            # assert False
            # process.kill()
            if process.returncode == None:
                print("PID:",process.pid)
                print("PGID:",os.getpgid(process.pid))
                # breakpoint()
                print('breakpoint')
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                # breakpoint()
                # os.killpg(process.pid, signal.SIGTERM)
                # assert False

        await process.wait()

        # fuck GCs, I want my destructors back
        # this .close() is being run by _transport.__del__() as well,
        # but closing it requires operation on the event loop
        # and issue with that is, when that event loop is already closed
        # so I have to close it here manually
        process._transport.close()  # type: ignore

        stdout: bytes = b"".join(stdout_chunks)
        stderr: bytes = b"".join(stderr_chunks)

        if isinstance(input, str):
            stdout = stdout.decode("utf-8")  # type: ignore
            stderr = stderr.decode("utf-8")  # type: ignore

        return (process.returncode, stdout, stderr, flags["timed_out"])

    async def bash_run(
        self, input, args
    ) -> Tuple[int | None, bytes | str, bytes | str, bool]:
        return await self.run(input, args)