from dataclasses import dataclass, field
from typing import List, Mapping


@dataclass
class OutputSnapshot:
    stdout: bytes
    stderr: bytes
    exit_code: int | None
    timed_out: bool
    artifacts: Mapping[str, bytes] = field(default_factory=dict)


@dataclass
class InputSnapshot:
    stdin: bytes
    args: List[bytes] = field(default_factory=list)
    timeout: int | float = 5000
    env: Mapping[bytes, bytes | None] = field(default_factory=dict)
    artifact_paths: Mapping[str, bytes] = field(default_factory=dict)
