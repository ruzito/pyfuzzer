from dataclasses import dataclass
from typing import List, Mapping

@dataclass
class OutputSnapshot:
    stdout: bytes
    stderr: bytes
    exit_code: int|None
    timed_out: bool
    artifacts: List[bytes] = []


@dataclass
class InputSnapshot:
    stdin: bytes
    args: List[bytes]
    env: Mapping[bytes, bytes|None]
    timeout: int|float
    artifact_paths: List[bytes] = []

