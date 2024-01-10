from hypothesis import given, settings, strategies as st

from generators import *

@given(st.integers(min_value=1, max_value=1000000), st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=256))
@settings(max_examples=1)
def test_bytes(length, range_begin, range_end):
        if range_begin == range_end:
                range_end += 1
        if range_begin > range_end:
                (range_begin, range_end) = (range_end, range_begin)
        x = random_bytes(length, (range_begin, range_end))
        assert(length == len(x))
        print(len(x))
        for b in x:
                assert(b >= range_begin)
                assert(b < range_end)