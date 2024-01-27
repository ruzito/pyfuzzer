import textwrap


def dedent(txt, trailing_ws="\n", leading_ws=""):
    return leading_ws + textwrap.dedent(txt).strip() + trailing_ws
