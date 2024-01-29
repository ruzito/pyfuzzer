import pytest
import re

from minimizer import BinaryMinimizer, minimizer_loop, MinimizerRunner
from snapshot import InputSnapshot, OutputSnapshot


class RegexOracle(MinimizerRunner):
    def __init__(self, regex):
        self.regex = regex

    async def run(self, input):
        if len(input.stdin) <= 0:
            return False
        return re.match(self.regex, input.stdin.decode("utf-8"))

    def get_last_output(self) -> OutputSnapshot | None:
        return None


@pytest.mark.parametrize(
    "granularity, segment, complement, expected",
    [
        (1, 1, True, (InputSnapshot(b"Hello"), 12, 2)),
        (1, 0, True, (InputSnapshot(b" world"), 12, 2)),
        (1, 0, False, (InputSnapshot(b"Hello"), 12, 2)),
        (1, 1, False, (InputSnapshot(b" world"), 12, 2)),
        (0, 0, True, (InputSnapshot(b""), 12, 1)),
        (0, 0, False, (InputSnapshot(b""), 12, 1)),
    ],
)
def test_array_minimizer(granularity, segment, complement, expected):
    minim = BinaryMinimizer()
    b = InputSnapshot(stdin=b"Hello world")
    res = minim.minimize(b, granularity, segment, complement)
    assert expected == res


@pytest.mark.parametrize(
    "regex, expected, input",
    [
        (r".*x.*y.*", InputSnapshot(b"xy"), InputSnapshot(b"aaaxaaaaaayaaa")),
        (r".*aaa.*", InputSnapshot(b"aaa"), InputSnapshot(b"aaaxaaaaaayaaa")),
    ],
)
@pytest.mark.asyncio
async def test_minimizer_loop(regex, expected, input):
    minim = BinaryMinimizer()

    err_predicate = RegexOracle(regex)

    result = await minimizer_loop(input, err_predicate, minim)
    assert expected == result[0]
