from random import randint

from abc import ABC, abstractmethod

from snapshot import InputSnapshot


class Randomizer(ABC):
    @abstractmethod
    def get_input(self) -> InputSnapshot:
        pass


class HellRandomizer(Randomizer):
    def __init__(self, input):
        self.cnt = 0
        self.template = input

    def get_input(self) -> InputSnapshot:
        if self.cnt == 0:
            self.cnt += 1
            return InputSnapshot(
                stdin=b"qwertyuhellertyui",
                args=self.template.args,
                timeout=self.template.timeout,
                env=self.template.env,
                artifact_paths=self.template.artifact_paths,
            )

        self.cnt += 1
        return InputSnapshot(
            stdin=b"heaven",
            args=self.template.args,
            timeout=self.template.timeout,
            env=self.template.env,
            artifact_paths=self.template.artifact_paths,
        )


class ByteRandomizer(Randomizer):
    def __init__(self, input: InputSnapshot) -> None:
        self.min_size = 0
        self.max_size = 200
        self.min_byte = 0
        self.max_byte = 255
        self.template = input

    def get_input(self) -> InputSnapshot:
        stdin = bytes(
            [
                randint(self.min_byte, self.max_byte)
                for _ in range(randint(self.min_size, self.max_size))
            ]
        )
        return InputSnapshot(
            stdin=stdin,
            args=self.template.args,
            timeout=self.template.timeout,
            env=self.template.env,
            artifact_paths=self.template.artifact_paths,
        )


class CStrRandomizer(Randomizer):
    def __init__(self) -> None:
        self.min_size = 0
        self.max_size = 200
        self.min_char = 1
        self.max_char = 255

    def get_input(self) -> InputSnapshot:
        cstr = [
            randint(self.min_char, self.max_char)
            for _ in range(randint(self.min_size, self.max_size))
        ]
        cstr[-1] = 0
        return InputSnapshot(stdin=bytes(cstr))
