import re

from abc import ABC, abstractmethod

class Oracle(ABC):
    @abstractmethod
    def categorize(self, exit_code:int, stdout:bytes, stderr:bytes, timeout_flag:bool)->bytes:
        pass

def analyze_output(process):
    asan_error = re.search(r"ERROR: AddressSanitizer", process.stderr)
    return_code = process.returncode
    return {"asan_error": asan_error, "return_code": return_code}
