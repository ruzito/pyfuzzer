from copy import deepcopy

from abc import ABC, abstractmethod

class Minimizer(ABC):
        # when first called, granularity_level and segment_index should both be set to 0 which should always return (vec![], N, 1)
        # the function then returns the very first attempt at minimizing the payload
        # it also returns the number of granularity_levels for given payload and number of segments present in the payload given this granularity
        # caller can also specify if the function should return the chosen segment or it's complement
        #
        # if caller specifies granularity_level higher than allowed, minimizer will assume the granularity_level to be the largest possible
        # if caller specifies segment_index higher than allowed, minimizer will choose the last segment
        #
        # Can never return the same payload as the one given (could lead to infinite loops)
        #
        # @returns (minimized_payload, number_of_granularity_levels)
        @abstractmethod
        def minimize(self, payload, granularity_level, segment_index, complement):
                pass

class BinaryMinimizer(Minimizer):
        def minimize(self, payload, granularity_level, segment_index, complement):
                length = len(payload)
                number_of_granularity_levels = length + 1
                if granularity_level == 0 and segment_index == 0:
                        return ([], number_of_granularity_levels, 1)

                granularity = min(granularity_level,number_of_granularity_levels - 1)
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
                        res = (before_slice + after_slice, number_of_granularity_levels, number_of_segments)
                else:
                        res = (segment_slice, number_of_granularity_levels, number_of_segments)

                return res

def minimizer_loop(input, runner, minimizer: Minimizer):
        # copy base payload
        base_payload = deepcopy(input)

        # granularity_level, segment_index
        variant_iter_end = (1,1)
        variant_iter = (0,0)

        def succ(it_opt, end):
                if it_opt == None:
                        return None
                it = it_opt
                if end[0] < 1 or end[1] < 1:
                        return None
                if it[0] >= end[0] - 1 and it[1] >= end[1] - 1:
                        return None
                if it[1] >= end[1] - 1:
                        return (it[0] + 1, 0)
                return (it[0], it[1] + 1)

        # let mut last_size = usize::MAX;
        # let mut stuck_count = 0_usize;

        while variant_iter != None:
                variant_iter
                x = minimizer.minimize(base_payload, variant_iter[0], variant_iter[1], True);
                variant_iter_end = (x[1], x[2])
                hit = runner(x[0])
                same = base_payload == x[0]
                if hit and not same:
                        # hit
                        base_payload = x[0]
                        variant_iter = (0,0)
                        variant_iter_end = (1,1)
                        # if last_size > base_payload.len() {last_size = base_payload.len(); stuck_count = 0;}
                        # stuck_count += 1;
                        # if stuck_count > 10 {std::process::exit(42);}
                        # println!("minimizing hit: {}: ({},{})", &base_payload.len(), variant_iter.unwrap().0, variant_iter.unwrap().1);
                else:
                        # miss
                        variant_iter = succ(variant_iter, variant_iter_end)

        return base_payload
