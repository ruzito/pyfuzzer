import pytest
import re

from minimizer import *

@pytest.mark.parametrize("granularity, segment, complement, result", [
        (1, 1, True, (b"Hello", 12, 2)),
        (1, 0, True, (b" world", 12, 2)),
        (1, 0, False, (b"Hello", 12, 2)),
        (1, 1, False, (b" world", 12, 2)),
        (0, 0, True, ([], 12, 1)),
        (0, 0, False, ([], 12, 1)),
])
def test_array_minimizer(granularity, segment, complement, result):
        minim = BinaryMinimizer()
        b = b"Hello world"
        res = minim.minimize(b, granularity, segment, complement)
        assert result == res

@pytest.mark.parametrize("regex, expected, input", [
        (r'.*x.*y.*', "xy", "aaaxaaaaaayaaa"),
        (r'.*aaa.*', "aaa", "aaaxaaaaaayaaa")
])
def test_minimizer_loop(regex, expected, input):
        minim = BinaryMinimizer()
        def err_predicate(arr):
                if len(arr) <= 0:
                        return False
                return re.match(regex, arr)
        
        result = minimizer_loop(input, err_predicate, minim)
        assert expected == result