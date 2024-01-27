from copy import deepcopy

from abc import ABC, abstractmethod
from typing import Tuple
from snapshot import InputSnapshot

class MinimizerRunner(ABC):
    # Should return true if the minimizer should assume the run was a hit
    # Should return false otherwise
    @abstractmethod
    async def run(self, input: InputSnapshot) -> bool:
        pass


class Minimizer(ABC):
    # When first called, granularity_level and segment_index should both be set to 0
    # which should always return `(vec![], N, 1)`.
    # The function then returns the very first attempt at minimizing the payload
    # it also returns the number of granularity_levels for given payload and number of segments
    # present in the payload given this granularity
    # caller can also specify if the function should return the chosen segment or it's complement
    #
    # If caller specifies granularity_level higher than allowed, minimizer will assume
    # the granularity_level to be the largest possible.
    # If caller specifies segment_index higher than allowed, minimizer will choose the last segment
    #
    # Can never return the same payload as the one given (could lead to infinite loops)
    #
    # @returns (minimized_payload, number_of_granularity_levels)
    @abstractmethod
    def minimize(
        self,
        payload: InputSnapshot,
        granularity_level: int,
        segment_index: int,
        complement: bool,
    ) -> Tuple[InputSnapshot, int, int]:
        pass


class BinaryMinimizer(Minimizer):
    def minimize(
        self,
        input: InputSnapshot,
        granularity_level: int,
        segment_index: int,
        complement: bool,
    ) -> Tuple[InputSnapshot, int, int]:
        def create_snapshot(stdin:bytes)->InputSnapshot:
            return InputSnapshot(
                stdin=stdin,
                args=input.args,
                timeout=input.timeout,
                env=input.env,
                artifact_paths=input.artifact_paths
            )
        payload = input.stdin
        length = len(payload)
        number_of_granularity_levels = length + 1
        if granularity_level == 0 and segment_index == 0:
            return (create_snapshot(b''), number_of_granularity_levels, 1)

        granularity = min(granularity_level, number_of_granularity_levels - 1)
        number_of_segments = granularity + 1
        index = min(number_of_segments, segment_index)

        segment_size = length // number_of_segments

        segment_begin = index * segment_size
        if index < (number_of_segments - 1):
            segment_end = (index + 1) * segment_size
        else:
            segment_end = length

        before_slice = payload[0:segment_begin]
        segment_slice = payload[segment_begin:segment_end]
        after_slice = payload[segment_end:length]

        if complement:
            res = (
                create_snapshot(before_slice + after_slice),
                number_of_granularity_levels,
                number_of_segments,
            )
        else:
            res = (create_snapshot(segment_slice), number_of_granularity_levels, number_of_segments)

        return res


async def minimizer_loop(input: InputSnapshot, runner: MinimizerRunner, minimizer: Minimizer):
    # copy base payload
    base_payload = deepcopy(input)

    # granularity_level, segment_index
    variant_iter_end = (1, 1)
    variant_iter = (0, 0)

    def succ(it_opt, end):
        if it_opt is None:
            return None
        it = it_opt
        if end[0] < 1 or end[1] < 1:
            return None
        if it[0] >= end[0] - 1 and it[1] >= end[1] - 1:
            return None
        if it[1] >= end[1] - 1:
            return (it[0] + 1, 0)
        return (it[0], it[1] + 1)

    while variant_iter is not None:
        x = minimizer.minimize(base_payload, variant_iter[0], variant_iter[1], True)
        variant_iter_end = (x[1], x[2])
        hit = await runner.run(x[0])
        same = base_payload == x[0]
        if hit and not same:
            # hit
            base_payload = x[0]
            variant_iter = (0, 0)
            variant_iter_end = (1, 1)
        else:
            # miss
            variant_iter = succ(variant_iter, variant_iter_end)

    return base_payload
