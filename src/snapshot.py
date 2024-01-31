from dataclasses import dataclass, field


@dataclass
class OutputSnapshot:
    stdout: bytes
    stderr: bytes
    exit_code: int | None
    timed_out: bool
    time: float
    artifacts: dict[str, bytes] = field(default_factory=dict)


@dataclass
class InputSnapshot:
    stdin: bytes
    args: list[bytes]
    timeout: int | float = 5000
    env: dict[bytes, bytes | None] = field(default_factory=dict)
    artifact_paths: dict[str, bytes] = field(default_factory=dict)


# This is just a proof of concept for now
class TreeInputSnapshot(InputSnapshot):
    def __init__(self, tree):
        self.tree = tree

    @property
    def stdin(self) -> bytes:
        return self.render(self.tree)

    @stdin.setter
    def stdin(self, val):
        assert False, "Do not set the rendered stdin of a tree based input"

    def render(self, tree) -> bytes:
        return b""

    def get_tree(self):
        return self.tree

    def set_tree(self, tree):
        self.tree = tree


@dataclass
class RunSnapshot:
    input: InputSnapshot
    output: OutputSnapshot
