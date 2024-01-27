import pytest
import re

from minimizer import BinaryMinimizer, minimizer_loop, MinimizerRunner

class RegexOracle(MinimizerRunner):
    def __init__(self, regex):
        self.regex = regex

    async def run(self, input):
        if len(input) <= 0:
            return False
        return re.match(self.regex, input)

@pytest.mark.parametrize(
    "granularity, segment, complement, result",
    [
        (1, 1, True, (b"Hello", 12, 2)),
        (1, 0, True, (b" world", 12, 2)),
        (1, 0, False, (b"Hello", 12, 2)),
        (1, 1, False, (b" world", 12, 2)),
        (0, 0, True, (b'', 12, 1)),
        (0, 0, False, (b'', 12, 1)),
    ],
)
def test_array_minimizer(granularity, segment, complement, result):
    minim = BinaryMinimizer()
    b = b"Hello world"
    res = minim.minimize(b, granularity, segment, complement)
    assert result == res


@pytest.mark.parametrize(
    "regex, expected, input",
    [(r".*x.*y.*", "xy", "aaaxaaaaaayaaa"), (r".*aaa.*", "aaa", "aaaxaaaaaayaaa")],
)
@pytest.mark.asyncio
async def test_minimizer_loop(regex, expected, input):
    minim = BinaryMinimizer()

    err_predicate = RegexOracle(regex)

    result = await minimizer_loop(input, err_predicate, minim)
    assert expected == result
