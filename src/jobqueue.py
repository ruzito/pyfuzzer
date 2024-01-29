import asyncio

# import utils
from abc import ABC, abstractmethod

from functools import total_ordering


@total_ordering
class AsyncJob(ABC):
    # When first called, granularity_level and segment_index should both be set to 0
    # which should always return `(vec![], N, 1)`.
    # The function then returns the very first attempt at minimizing the payload
    # it also returns the number of granularity_levels for given payload and number of segments
    # present in the payload given this granularity
    # caller can also specify if the function should return the chosen segment or it's complement
    #
    # If caller specifies granularity_level higher than allowed, minimizer will assume
    # the granularity_level to be the largest possible.
    # If caller specifies segment_index higher than allowed, minimizer will choose the last segment
    #
    # Can never return the same payload as the one given (could lead to infinite loops)
    #
    # @returns (minimized_payload, number_of_granularity_levels)
    @abstractmethod
    async def run(self):
        pass

    def __eq__(self, other):
        return id(self) == id(other)

    def __lt__(self, other):
        return id(self) < id(other)


class JobQueueManager:
    def __init__(self, max_workers: int):
        self.workers: list[asyncio.Task[None]] = []
        self.sentinel = (99, None)
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.jobs: asyncio.Queue = asyncio.PriorityQueue()

    async def push(self, job: AsyncJob, priority=5):
        await self.jobs.put((priority, job))

    def abort(self, exc=[]):
        for worker_id, worker in enumerate(self.workers):
            if worker_id in exc:
                continue
            worker.cancel()
        self.workers = []

    async def worker(self, worker_id):
        # print("[{}]".format(worker_id), "Worker started")
        job = None

        def task_done():
            nonlocal job
            nonlocal self
            if job is not None:
                self.jobs.task_done()
                # print("[{}]".format(worker_id), "job done")
            job = None

        while True:
            try:
                # print("[{}]".format(worker_id), "recieving job ...")
                job = await self.jobs.get()
                # print("[{}]".format(worker_id), "recieved job:", job)
                if job == self.sentinel:
                    # print("[{}]".format(worker_id), "worker recieved sentinel")
                    break
                (priority, j) = job

                # print("[{}]".format(worker_id), "worker witing for semaphore ...")
                async with self.semaphore:
                    # print("[{}]".format(worker_id), "worker entered semaphore")
                    # print("[{}]".format(worker_id), "worker awaiting runner ...")
                    await j.run()
                    # print("[{}]".format(worker_id), "worker awaited runner")
            except BaseException as e:
                # breakpoint()
                # print("[{}]".format(worker_id), "exception raised:", e)
                self.abort(exc=[worker_id])
                raise e
            finally:
                task_done()
        task_done()

    async def run(self):
        self.start()
        await self.join()

    def start(self):
        for worker in self.workers:
            worker.cancel()
        self.workers = [
            asyncio.create_task(self.worker(i)) for i in range(self.max_workers)
        ]
        # for w in self.workers:
        #     utils.wrap_task(w)

    def empty(self):
        return self.jobs.empty()

    def clear(self):
        try:
            while True:
                self.jobs.get_nowait()
        except asyncio.QueueEmpty:
            pass

    def size(self):
        return self.jobs.qsize()

    async def join(self):
        for _ in range(self.max_workers):
            # print("putting sentinel ...")
            await self.jobs.put(self.sentinel)
            # print("put sentinel")
        # print("joining queue ...")
        results = await asyncio.gather(*self.workers, return_exceptions=True)
        for result in results:
            try:
                if isinstance(result, Exception):
                    raise result
            except (BrokenPipeError, ConnectionResetError):
                pass

        sz = self.size()
        if sz == 0:
            await self.jobs.join()
        else:
            raise Exception(
                "Could not finish {} jobs correctly, "
                "this is certainly a bug in the jobqueue. FIXME!".format(sz)
            )
        # print("joined queue")
