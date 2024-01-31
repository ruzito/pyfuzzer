import re

from abc import ABC, abstractmethod

from snapshot import InputSnapshot, OutputSnapshot


class Oracle(ABC):
    @abstractmethod
    async def categorize(self, output: OutputSnapshot) -> bytes | None:
        pass


def analyze_output(process):
    asan_error = re.search(r"ERROR: AddressSanitizer", process.stderr)
    return_code = process.returncode
    return {"asan_error": asan_error, "return_code": return_code}


class Runner(ABC):
    # Should return true if the minimizer should assume the run was a hit
    # Should return false otherwise
    @abstractmethod
    async def run(self, input: InputSnapshot) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def get_last_output(self) -> OutputSnapshot | None:
        pass  # pragma: no cover
