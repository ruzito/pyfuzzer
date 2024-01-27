_report: dict = {
    "generating": True,
    "minimization_queue": 0,
    "runs_total": 0,
    "runs_hanged": 0,
    "runs_failed": 0,
    "runs_succeeded": 0,
    "unique_failure_types": 0,
    "unique_failure_inputs_minimized": 0,
    "unique_hang_inputs_minimized": 0,
    "exec_time_avg": 0,
    "exec_time_avg_nohang": 0,
    # 'exec_time_median': 0, # dont want to update realtime
    # 'exec_time_median_nohang': 0, # dont want to update realtime
    "exec_time_min": 0,
    "exec_time_min_nohang": 0,
}


def render(crs):
    global _report
    height, width = crs.getmaxyx()

    stats = [
        ("Minimization queue:", f"{_report['minimization_queue']}"),
        ("Total runs:", f"{_report['runs_total']}"),
        ("Failed runs:", f"{_report['runs_failed']}"),
        ("Hanged runs:", f"{_report['runs_hanged']}"),
        ("Successfull runs:", f"{_report['runs_succeeded']}"),
        ("Unique failures:", f"{_report['unique_failure_types']}"),
        (
            "Unique fail-inputs:",
            f"{_report['unique_failure_inputs_minimized']} (after minimization)",
        ),
        (
            "Unique hang-inputs:",
            f"{_report['unique_hang_inputs_minimized']} (after minimization)",
        ),
        (
            "Exec time AVG:",
            f"{_report['exec_time_avg']}/{_report['exec_time_avg_nohang']} (all/nohang)",
        ),
        (
            "Exec time MIN:",
            f"{_report['exec_time_min']}/{_report['exec_time_min_nohang']} (all/nohang)",
        ),
    ]

    max_width_label = 0
    max_width_data = 0
    for s in stats:
        label_len = len(s[0])
        data_len = len(s[1])
        if max_width_label < label_len:
            max_width_label = label_len
        if max_width_data < data_len:
            max_width_data = data_len

    min_space = 1
    if height < len(stats) or width < (max_width_label + max_width_data + min_space):
        crs.addstr(0, 0, "MIN SIZ WRN")
        return

    for i in range(len(stats)):
        # print(stats[i][0], file=sys.stderr)
        crs.addstr(i, 0, stats[i][0])
        crs.addstr(i, max_width_label + min_space, stats[i][1])


def final_report():
    pass


def stop_generating():
    global _report
    _report["generating"] = False


def update_minimization_queue_size(sz: int):
    global _report
    _report["minimization_queue"] = sz


def update_failure_type_count(cnt: int):
    pass


def update_unique_minimized_failure_count(cnt: int):
    pass


def update_unique_minimized_hang_count(cnt: int):
    pass


def add_run(hang: bool, fail: bool, exec_time: int):
    global _report
    _report["runs_total"] += 1
    if hang:
        _report["runs_hanged"] += 1
    elif fail:
        _report["runs_failed"] += 1
    else:
        _report["runs_succeeded"] += 1
