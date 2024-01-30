import asyncio
import os
import signal
import sys
from snapshot import InputSnapshot, OutputSnapshot
import time
import seppuku

# import utils


async def _gather_artifacts(paths: dict[str, bytes]) -> dict[str, bytes]:
    # TODO: gather artifacts
    return {}


async def runexec(input: InputSnapshot) -> OutputSnapshot:
    # Run the subprocess with input
    start_time = time.perf_counter()
    # try:
    process = await asyncio.create_subprocess_exec(
        *input.args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True
    )
    seppuku.register_process(process)
    # except BaseException:
    #     print(input, file=sys.stderr)
    #     raise

    try:
        if process.stdin is not None:
            process.stdin.write(input.stdin)
            await process.stdin.drain()
            process.stdin.close()
    # No cover - flaky
    except (BrokenPipeError, ConnectionResetError):  # pragma: no cover
        pass
    # except BaseException:
    #     import traceback

    #     print(
    #         "Runner caught exception during attempt to write to stdin:\n{}".format(
    #             traceback.format_exc()
    #         )
    #     )
    #     pass

    async def read_stream(stream, chunks, chunk_sizes=1024):
        while True:
            chunk = await stream.read(chunk_sizes)
            if not chunk:
                break
            chunks.append(chunk)
            if stream.at_eof():
                return  # pragma: no cover

    # The following shannanigans are here to cope with the fact
    # that I want to be able to get stdout and stderr (at least partialy)
    # even if the cmd times out
    # And be able to have this as an async job that I can stuff into thread pool
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    stdout_task = asyncio.create_task(read_stream(process.stdout, stdout_chunks))
    stderr_task = asyncio.create_task(read_stream(process.stderr, stderr_chunks))
    # utils.wrap_task(stdout_task)
    # utils.wrap_task(stderr_task)

    flags = {"cb_run": False, "timed_out": False}

    def timeout_callback():
        flags["cb_run"] = True
        if stdout_task.done() and stderr_task.done():
            # No cover - flaky
            return  # pragma: no cover
        flags["timed_out"] = True
        stdout_task.cancel()
        stderr_task.cancel()

    loop = asyncio.get_event_loop()
    timeout_task = loop.call_later(input.timeout, timeout_callback)

    done, pending = await asyncio.wait(
        [stdout_task, stderr_task], return_when=asyncio.ALL_COMPLETED
    )

    if not flags["cb_run"]:
        timeout_task.cancel()

    if flags["timed_out"]:
        # assert False
        # process.kill()
        if process.returncode is None:
            # print("PID:", process.pid)
            # print("PGID:", os.getpgid(process.pid))
            # breakpoint()
            # print("breakpoint")
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # No cover - flaky
            except ProcessLookupError:  # pragma: no cover
                pass
            # breakpoint()
            # os.killpg(process.pid, signal.SIGTERM)
            # assert False

    await process.wait()
    seppuku.release_process(process)
    end_time = time.perf_counter_ns()
    perf_time = end_time - start_time
    print(*input.args, file=sys.stderr)
    print(process.returncode, file=sys.stderr)

    # fuck GCs, I want my destructors back
    # this .close() is being run by _transport.__del__() as well,
    # but closing it requires operation on the event loop
    # and issue with that is, when that event loop is already closed
    # so I have to close it here manually
    process._transport.close()  # type: ignore

    stdout: bytes = b"".join(stdout_chunks)
    stderr: bytes = b"".join(stderr_chunks)

    return OutputSnapshot(
        stdout=stdout,
        stderr=stderr,
        exit_code=process.returncode,
        timed_out=flags["timed_out"],
        time=perf_time,
        artifacts=await _gather_artifacts(input.artifact_paths),
    )


class BashRunner:
    def __init__(self, cmd, *, timeout: int | float = 5000):
        self.cmd = cmd
        self.timeout = timeout

    async def run(self, input, args):
        if isinstance(input, str):
            byte_input = input.encode("utf-8")
        elif isinstance(input, bytes):
            byte_input = input
        else:
            raise TypeError("Input must be a `str` or `bytes`")

        command = ["bash", "-c", self.cmd.format(**args)]

        out: OutputSnapshot = await runexec(
            InputSnapshot(
                stdin=byte_input,
                args=command,
                timeout=self.timeout,
            )
        )

        return (out.exit_code, out.stdout, out.stderr, out.timed_out)
