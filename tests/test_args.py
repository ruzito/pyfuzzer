import config
import pytest


def test_help():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--help"])
    assert e_info.value.code == 0


def test_required_input_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--generator=hell_mock", "--results=DUMMY", "--timeout=0"])
    assert e_info.value.code == 2


def test_required_generator_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--input-method=stdin", "--results=DUMMY", "--timeout=0"])
    assert e_info.value.code == 2


def test_required_results_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(["--input-method=stdin", "--generator=hell_mock", "--timeout=0"])
    assert e_info.value.code == 2


def test_required_timeout_method():
    with pytest.raises(SystemExit) as e_info:
        config.parse(
            ["--input-method=stdin", "--generator=hell_mock", "--results=DUMMY"]
        )
    assert e_info.value.code == 2


def test_stdin_input_method():
    opts = config.parse(
        [
            "--input-method=stdin",
            "--generator=hell_mock",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.input_method == config.InputMethod.STDIN


def test_file_input_method():
    opts = config.parse(
        [
            "--input-method=file",
            "--generator=hell_mock",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.input_method == config.InputMethod.FILE


def test_no_minimization():
    opts = config.parse(
        [
            "--input-method=stdin",
            "--generator=hell_mock",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.minimize is False


def test_minimization():
    opts = config.parse(
        [
            "--input-method=stdin",
            "--minimize",
            "--generator=hell_mock",
            "--results=DUMMY",
            "--timeout=0",
        ]
    )
    assert opts.minimize is True
