from minimizer import BinaryMinimizer, MinimizerRunner, Minimizer
from jobqueue import JobQueueManager, AsyncJob
from runner import Runner
from oracle import Oracle


class RandomInputJob(AsyncJob):
    def __init__(self, queue:JobQueueManager, oracle: Oracle, runner: Runner, input, args: dict):
        self.runner = runner
        self.input = input
        self.args = args
        self.queue = queue
        self.oracle = oracle

    async def run(self):
        result = await self.runner.bash_run(self.input, self.args)
        (ret, stdout, stderr, timeout_flag) = result
        if ret is None:
            ret = 666
        if isinstance(stdout, str):
            stdout = stdout.encode('utf-8')
        if isinstance(stderr, str):
            stderr = stderr.encode('utf-8')
        hash:bytes = self.oracle.categorize(ret, stdout, stderr, timeout_flag)

class MinimizeInputJob(AsyncJob):
    def __init__(self, runner: Runner, minimizer: Minimizer, snapshot):
        self.runner = runner
        self.input = input

    async def run(self):
        result = await self.runner.bash_run(self.input, self.args)


class Application:
    def __init__(self):
        self.workers = 5
        self.queue = JobQueueManager(self.workers)
        self.queue.start()
        self.runner = Runner("sleep 4")

    async def generate_stage(self):
        # Get random input
        # Run input
        # Oracle result
        # Cache category
        # Potentially schedule category

    async def minimize_stage(self):
        # TODO: await self.queue.join()
        pass

    def defer_exit(self) -> bool:
        return True


_app = Application()


async def loop(stage):
    """
    stage == 0 means we should generate random input
    stage == 1 means we should only minimize

    @param stage
    @returns False when the app is ready to be stopped

    TODO: generate input, add it to queue, add minimize cb
    """
    global _app
    if stage == 0:
        await _app.generate_stage()
    elif stage == 1:
        await _app.minimize_stage()

    return _app.defer_exit()
