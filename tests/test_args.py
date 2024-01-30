import config
import pytest


def test_help():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--help"])
    assert e_info.value.code == 0


def test_exclusive_input_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(
            [
                "--stdin",
                "--file",
                "--generator=DUMMY",
                "--generator=DUMMY",
                "--results=DUMMY",
                "--timeout=0",
            ]
        )
    assert e_info.value.code == 2


def test_required_input_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(
            ["--generator=DUMMY", "--generator=DUMMY", "--results=DUMMY", "--timeout=0"]
        )
    assert e_info.value.code == 2


def test_required_generator_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--stdin", "--results=DUMMY", "--timeout=0"])
    assert e_info.value.code == 2


def test_required_results_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--stdin", "--generator=DUMMY", "--timeout=0"])
    assert e_info.value.code == 2


def test_required_timeout_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--stdin", "--generator=DUMMY", "--results=DUMMY"])
    assert e_info.value.code == 2


def test_stdin_input_method():
    opts, _ = config.parse(
        [
            "--stdin",
            "--generator=DUMMY",
            "--generator=DUMMY",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.input_method == config.InputMethod.STDIN


def test_file_input_method():
    opts, _ = config.parse(
        [
            "--file",
            "--generator=DUMMY",
            "--generator=DUMMY",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.input_method == config.InputMethod.FILE


def test_no_minimization():
    opts, _ = config.parse(
        [
            "--stdin",
            "--generator=DUMMY",
            "--generator=DUMMY",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.minimizer is None


def test_minimization():
    opts, _ = config.parse(
        [
            "--stdin",
            "--minimizer=Dummy",
            "--generator=DUMMY",
            "--generator=DUMMY",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.minimizer is not None
