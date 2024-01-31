from asyncio import sleep
import asyncio
from minimizer import BinaryMinimizer, Runner, Minimizer, minimizer_loop
from jobqueue import JobQueueManager, AsyncJob
from randomizer import CStrRandomizer, ByteRandomizer, Randomizer, HellRandomizer
from runner import runexec
from utils import bash
from oracle import Oracle
from snapshot import InputSnapshot, OutputSnapshot, RunSnapshot
from dataclasses import dataclass
from report import update_minimization_queue_size, add_run
import config


@dataclass
class ApplicationContext:
    job_queue: JobQueueManager
    minimizer: Minimizer | None
    oracle: Oracle
    unique_errors: dict[bytes, RunSnapshot]
    unique_errors_minimized: dict[bytes, RunSnapshot]
    randomizer: Randomizer
    minimization_queue_size: int = 0


def options_to_context(opts: config.Options) -> ApplicationContext:
    cmd_str = opts.command
    cmd = bash(cmd_str)
    template_input = InputSnapshot(
        stdin=b"", args=cmd, timeout=opts.timeout
    )
    rnd: Randomizer
    minm: Minimizer | None
    orcl: Oracle = MyOracle()
    if opts.generator == config.InputType.HELL_MOCK:
        rnd = HellRandomizer(template_input)
        minm = BinaryMinimizer()
    elif opts.generator == config.InputType.BYTES:
        rnd = ByteRandomizer(template_input)
        minm = BinaryMinimizer()
    elif opts.generator == config.InputType.CSTR:
        rnd = CStrRandomizer(template_input)
        minm = BinaryMinimizer()
    else:
        raise NotImplementedError

    if not opts.minimize:
        minm = None

    return ApplicationContext(
        job_queue=JobQueueManager(max_workers=opts.workers),
        minimizer=minm,
        oracle=orcl,
        unique_errors={},
        unique_errors_minimized={},
        randomizer=rnd,
    )


async def attempt_run(
    input: InputSnapshot, context: ApplicationContext
) -> tuple[bytes | None, OutputSnapshot]:
    result: OutputSnapshot = await runexec(input)
    hsh: bytes | None = await context.oracle.categorize(result)
    add_run(result.timed_out, hsh is not None, result.time)
    if hsh is not None and hsh not in context.unique_errors:
        context.unique_errors[hsh] = RunSnapshot(input, result)
        update_minimization_queue_size(1)
        await context.job_queue.push(MinimizeInputJob(input, context, hsh))
    return (hsh, result)


class OracleRunner(Runner):
    def __init__(self, context: ApplicationContext, hsh: bytes):
        self.context = context
        self.hash = hsh
        self.last_output: None | OutputSnapshot = None

    async def run(self, input: InputSnapshot) -> bool:
        await sleep(5)
        (hsh, out) = await attempt_run(input, self.context)
        hit: bool = hsh is not None and self.hash == hsh
        self.last_output = out
        return hit

    def get_last_output(self):
        return self.last_output


class MinimizeInputJob(AsyncJob):
    def __init__(self, input: InputSnapshot, context: ApplicationContext, hsh: bytes):
        self.input = input
        self.context = context
        self.hash = hsh

    async def run(self):
        if self.context.minimizer is None:
            update_minimization_queue_size(-1)
            return

        result_input, result_output = await minimizer_loop(
            self.input,
            OracleRunner(self.context, self.hash),
            self.context.minimizer,
        )
        if result_output is None:
            assert result_input == self.context.unique_errors[self.hash].input, (
                "If result_output is None, that should mean minimization "
                "failed and should have returned the same InputSnapshot"
            )
            self.context.unique_errors_minimized[
                self.hash
            ] = self.context.unique_errors[self.hash]
        else:
            self.context.unique_errors_minimized[self.hash] = RunSnapshot(
                input=result_input, output=result_output
            )
        update_minimization_queue_size(-1)


class RandomInputJob(AsyncJob):
    def __init__(self, input: InputSnapshot, context: ApplicationContext):
        self.input = input
        self.context = context

    async def run(self):
        await attempt_run(self.input, self.context)


class MyOracle(Oracle):
    async def categorize(self, output: OutputSnapshot) -> bytes | None:
        if b"hell" in output.stdout:
            return b"hell"
        return None


class Application:
    def __init__(self):
        self.defer_exit_flag = True
        opts = config.get()
        self.context = options_to_context(opts)
        self.workers = opts.workers
        self.context.job_queue.start()

    async def generate_stage(self):
        if self.context.job_queue.size() > (self.workers * 5):
            # Ignore if the queue starts growing
            return

        input = self.context.randomizer.get_input()
        await self.context.job_queue.push(RandomInputJob(input, self.context))

    async def minimize_stage(self):
        await self.context.job_queue.ensure_sentinels()
        if self.context.job_queue.done():
            await self.context.job_queue.join()
            self.defer_exit_flag = False
        else:
            await sleep(0.25)

    async def soft_stop(self):
        if not self.context.job_queue.empty():
            await self.context.job_queue.clear_and_quit()

    async def hard_stop(self):
        self.context.job_queue.abort()
        if not self.context.job_queue.empty():
            await self.context.job_queue.clear_and_quit()
        self.defer_exit_flag = False

    def defer_exit(self) -> bool:
        return self.defer_exit_flag


_app = None


async def loop(stage):
    """
    @param stage
    @returns False when the app is ready to be stopped

    TODO: generate input, add it to queue, add minimize cb
    """
    global _app
    if _app is None:
        _app = Application()

    if stage == 0:
        await _app.generate_stage()
    elif stage == 1:
        await _app.minimize_stage()
    elif stage == 2:
        # await _app.soft_stop()
        # else:
        await _app.hard_stop()
        return False

    return _app.defer_exit()
