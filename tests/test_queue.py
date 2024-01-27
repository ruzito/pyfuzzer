import pytest
import asyncio

from jobqueue import JobQueueManager, AsyncJob
from runner import Runner

class RunnerJob(AsyncJob):
    def __init__(self, runner: Runner, input, args: dict, cb=None):
        self.runner = runner
        self.input = input
        self.args = args
        self.cb = cb

    async def run(self):
        result = await self.runner.bash_run(self.input, self.args)
        if self.cb is not None:
            await self.cb(result)


@pytest.mark.timeout(1.5)
@pytest.mark.asyncio
async def test_job_queue():
    MAX_WORKERS = 50  # Set the maximum number of concurrent workers
    number_of_jobs = 500  # Define how many jobs you want to run

    job_manager = JobQueueManager(MAX_WORKERS)

    # Start job manager
    job_manager.start()

    async def assert_job_result(result):
        (returncode, stdout, stderr, timed_out) = result
        assert returncode == 0
        assert stdout == "Hello world\n"
        assert stderr == ""
        assert not timed_out

    # Create Runner instances and enqueue jobs
    for i in range(number_of_jobs):
        runner = Runner(cmd="sleep 0.1; echo 'Hello world'")
        await job_manager.push(RunnerJob(
            runner, input="", args={}, cb=assert_job_result
        ))

    # Wait until all jobs are completed
    await job_manager.join()

@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_job_queue_timeout():
    MAX_WORKERS = 50  # Set the maximum number of concurrent workers
    number_of_jobs = 100  # Define how many jobs you want to run

    job_manager = JobQueueManager(MAX_WORKERS)

    # Start job manager
    job_manager.start()

    async def assert_job_result(result):
        (returncode, stdout, stderr, timed_out) = result
        assert stdout == "Hello world\n"
        assert timed_out

    # Create Runner instances and enqueue jobs
    for i in range(number_of_jobs):
        runner = Runner(cmd="echo 'Hello world'; sleep 300; echo 'Hello hell'", timeout=0.1)
        await job_manager.push(RunnerJob(
            runner, input="", args={}, cb=assert_job_result
        ))

    # Wait until all jobs are completed
    await job_manager.join()

@pytest.mark.timeout(2)
@pytest.mark.asyncio
async def test_job_queue_some_timeout():
    MAX_WORKERS = 50  # Set the maximum number of concurrent workers
    number_of_jobs = 100  # Define how many jobs you want to run

    job_manager = JobQueueManager(MAX_WORKERS)

    # Start job manager
    job_manager.start()

    async def assert_job_timed_out(result):
        (returncode, stdout, stderr, timed_out) = result
        assert stdout == "Hello world\n"
        assert timed_out

    async def assert_job_success(result):
        (returncode, stdout, stderr, timed_out) = result
        assert returncode == 0
        assert stdout == "Hello world\n"
        assert stderr == ""
        assert not timed_out

    # Create Runner instances and enqueue jobs
    for i in range(number_of_jobs//2):
        runner = Runner(cmd="echo 'Hello world'; sleep 300; echo 'Hello hell'", timeout=0.3)
        await job_manager.push(RunnerJob(
            runner, input="", args={}, cb=assert_job_timed_out
        ))

    # Create Runner instances and enqueue jobs
    for i in range(number_of_jobs//2):
        runner = Runner(cmd="sleep 0.1; echo 'Hello world'")
        await job_manager.push(RunnerJob(
            runner, input="", args={}, cb=assert_job_success
        ))

    # Wait until all jobs are completed
    await job_manager.join()


@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_empty_job_queue():
    MAX_WORKERS = 2  # Set the maximum number of concurrent workers

    job_manager = JobQueueManager(MAX_WORKERS)

    # Start job manager
    job_manager.start()

    await asyncio.sleep(1)

    async def assert_job_result(result):
        (returncode, stdout, stderr, timed_out) = result
        assert stdout == "Hello world\n"
        assert not timed_out

    runner = Runner(cmd="echo 'Hello world'")
    await job_manager.push(RunnerJob(
        runner, input="", args={}, cb=assert_job_result
    ))

    # Wait until all jobs are completed
    await job_manager.join()


@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_empty_job_queue_exceptions():
    MAX_WORKERS = 2  # Set the maximum number of concurrent workers

    job_manager = JobQueueManager(MAX_WORKERS)

    # Start job manager
    job_manager.start()

    await asyncio.sleep(1)

    async def assert_job_result(result):
        (returncode, stdout, stderr, timed_out) = result
        assert stdout == "Hello world\n"
        assert timed_out

    runner = Runner(cmd="echo 'Hello world'")
    await job_manager.push(RunnerJob(
        runner, input="", args={}, cb=assert_job_result
    ))

    # Wait until all jobs are completed
    with pytest.raises(AssertionError) as _:
        await job_manager.join()

