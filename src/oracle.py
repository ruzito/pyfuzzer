import re

from abc import ABC, abstractmethod

from snapshot import OutputSnapshot

class Oracle(ABC):
    @abstractmethod
    def categorize(
        self, output: OutputSnapshot
    ) -> bytes:
        pass


def analyze_output(process):
    asan_error = re.search(r"ERROR: AddressSanitizer", process.stderr)
    return_code = process.returncode
    return {"asan_error": asan_error, "return_code": return_code}
