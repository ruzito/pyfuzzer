from minimizer import BinaryMinimizer, MinimizerRunner, Minimizer
from jobqueue import JobQueueManager, AsyncJob
from runner import runexec
from oracle import Oracle
from snapshot import InputSnapshot, OutputSnapshot

class RandomInputJob(AsyncJob):
    def __init__(self, queue:JobQueueManager, oracle: Oracle, input: InputSnapshot, args: dict):
        self.input = input
        self.args = args
        self.queue = queue
        self.oracle = oracle

    async def run(self):
        result:OutputSnapshot = await runexec(self.input)
        hash:bytes = self.oracle.categorize(result)

class MinimizeInputJob(AsyncJob):
    def __init__(self, input: InputSnapshot, minimizer: Minimizer, minimizer_runner):
        self.input = input

    async def run(self):
        result = await runexec(self.input)


class Application:
    def __init__(self):
        self.workers = 5
        self.queue = JobQueueManager(self.workers)
        self.queue.start()

    async def generate_stage(self):
        # Get random input
        # Run input
        # Oracle result
        # Cache category
        # Potentially schedule category
        pass

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
