import os
import pytest

from hypothesis import given, strategies as st
from test_utils import dedent

from runner import Runner


@pytest.mark.asyncio
async def test_runner_basic():
    runner = Runner("cat | grep '{regex}'")
    (exit_code, std_out, std_err, timed_out) = await runner.bash_run(
        "Hello\nworld", {"regex": "ell"}
    )
    assert not timed_out
    assert exit_code == 0
    assert std_out == "Hello\n"
    assert std_err == ""


@pytest.mark.asyncio
async def test_runner_error():
    runner = Runner("cat | grep '{regex}'")
    (exit_code, std_out, std_err, timed_out) = await runner.bash_run(
        "Hello\nworld", {"regex": "-g"}
    )
    assert not timed_out
    assert exit_code == 2
    assert std_out == ""
    assert std_err == dedent(
        """
        grep: invalid option -- 'g'
        Usage: grep [OPTION]... PATTERNS [FILE]...
        Try 'grep --help' for more information.
        """
    )


@pytest.mark.asyncio
async def test_runner_redirection():
    file_path = "./tests/artifacts/hello_world.log"
    expected_contents = "Hello, this is the expected file content.\n"
    runner = Runner("mkdir -p ./tests/artifacts/ ; echo -n '{content}' > {file}")
    (exit_code, std_out, std_err, timed_out) = await runner.bash_run(
        "", {"file": file_path, "content": expected_contents}
    )
    assert not timed_out
    assert exit_code == 0
    assert std_out == ""
    assert std_err == ""
    assert os.path.exists(file_path), f"File does not exist: {file_path}"

    with open(file_path, "r") as file:
        assert (
            expected_contents == file.read()
        ), "File contents do not match the expected contents."


class TestRepeatedExecution:
    @pytest.fixture(scope="class")
    def cat_runner(self):
        return Runner("cat")

    @pytest.mark.asyncio
    @given(st.text())
    async def test_text(self, cat_runner, text):
        (exit_code, std_out, std_err, timed_out) = await cat_runner.bash_run(text, {})
        assert not timed_out
        assert exit_code == 0
        assert std_out == text
        assert std_err == ""

    @pytest.mark.asyncio
    @given(st.binary())
    async def test_bytes(self, cat_runner, text):
        (exit_code, std_out, std_err, timed_out) = await cat_runner.bash_run(text, {})
        assert not timed_out
        assert exit_code == 0
        assert std_out == text
        assert std_err == b""


@pytest.mark.asyncio
async def test_runner_type_error():
    runner = Runner("cat")
    with pytest.raises(TypeError) as _:
        (exit_code, std_out, std_err, timed_out) = await runner.bash_run(34, {})


@pytest.mark.asyncio
async def test_runner_timeout():
    runner = Runner("sleep 3000", timeout=0.25)
    (exit_code, std_out, std_err, timed_out) = await runner.bash_run("", {})
    assert timed_out


@pytest.mark.asyncio
async def test_runner_timeout_split_output():
    runner = Runner("echo 'Hello world' ; sleep 20 ; echo 'Fork'", timeout=1)
    (exit_code, std_out, std_err, timed_out) = await runner.bash_run("", {})
    assert timed_out
    assert std_out == "Hello world\n"
