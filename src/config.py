import argparse
from typing import Sequence
from enum import Enum

_options = None
_command = None


class InputMethod(Enum):
    STDIN = 1
    FILE = 2


def parse(args: Sequence[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="Random Fuzzing Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stdin",
        action="store_const",
        dest="input_method",
        const=InputMethod.STDIN,
        help="Fuzz through stdin",
    )
    group.add_argument(
        "--file",
        action="store_const",
        dest="input_method",
        const=InputMethod.FILE,
        help="Fuzz through file",
    )
    parser.add_argument(
        "--generator",
        required=True,
        nargs=1,
        type=str,
        help="Which random generator to use",
    )
    parser.add_argument(
        "--results", required=True, nargs=1, type=str, help="Where to store results"
    )
    parser.add_argument(
        "--timeout",
        required=True,
        nargs=1,
        type=int,
        help="Timeout after which assume the program has hanged",
    )
    parser.add_argument(
        "--minimizer",
        nargs=1,
        type=str,
        help="Which minimizer to use, if one should be used",
    )

    return parser.parse_known_args(args)


def init():
    global _options
    global _command
    _options, _command = parse()  # pragma: no cover
