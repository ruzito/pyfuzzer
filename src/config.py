import argparse
from dataclasses import dataclass
from typing import Sequence
from enum import Enum


class InputMethod(Enum):
    STDIN = 1
    FILE = 2


class InputType(Enum):
    BYTES = 1
    CSTR = 2
    HELL_MOCK = 666


@dataclass
class Options:
    input_method: InputMethod
    minimize: bool
    generator: InputType
    results: str
    timeout: int
    workers: int
    command: str


_options: Options | None = None


class Args(argparse.ArgumentParser):
    def add_enum(self, opt: str, enum: type[Enum], **kwargs):
        def tp(s: str):
            return s.lower()

        class EnumAction(argparse.Action):
            def __call__(self, parser, namespace, value, option_string=None):
                # Set the enum instance to the namespace
                enum_val = None
                for k, _ in enum.__members__.items():
                    if k.lower() == value.lower():
                        enum_val = enum[k]
                setattr(namespace, self.dest, enum_val)

        self.add_argument(
            opt,
            type=tp,
            action=EnumAction,
            choices=[e.name.lower() for e in enum],
            **kwargs
        )


def parse(args: Sequence[str] | None = None) -> Options:
    parser = Args(description="Random Fuzzing Tool")
    parser.add_enum("--generator", InputType, required=True)
    parser.add_enum("--input-method", InputMethod, required=True)
    parser.add_argument(
        "--results", required=True, nargs=1, type=str, help="Where to store results"
    )
    parser.add_argument(
        "--timeout",
        required=True,
        # nargs=1,
        type=int,
        help="Timeout after which assume the program has hanged",
    )
    parser.add_argument(
        "--workers",
        required=True,
        # nargs=1,
        type=int,
        help="How many parallel instances of the fuzzed program to run at most",
    )
    parser.add_argument(
        "--minimize",
        action="store_true",
        help="Determines wether failures should be minimized, "
        "this can cause a significant performance hit",
        default=False,
    )
    parser.add_argument(
        "command",
        type=str,
        # nargs=1,
        help="command to test, add environment variable $PYFUZZ_FILE "
        "if you use the `file` input mehod",
    )

    opts = parser.parse_args(args)
    return Options(**vars(opts))


def init():
    global _options
    _options = parse()


def get() -> Options:
    global _options
    if _options is None:
        init()
    return _options  # type: ignore
