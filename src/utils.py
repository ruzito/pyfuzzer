import sys


def bash(cmd: str):
    return [b"bash", b"-c", str.encode("utf-8")]


def handle_task_exception(task):
    try:
        task.result()
    except BaseException as e:
        print(f"Exception in task: {e}", file=sys.stderr)


def wrap_task(task):
    task.add_done_callback(handle_task_exception)
