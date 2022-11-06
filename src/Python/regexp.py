#!/usr/bin/env python3

import re
from run import run_approx_raw
from sys import argv


def init_regexp(pattern, k):
    # Create the regular expression for this pattern
    regexp = pattern[0]
    for char in pattern[1:]:
        regexp += f"[^{char}]{{0,{k}}}{char}"
    regexp = f"(?={regexp})"

    return [regexp]


def regexp(pat_data, sequence):
    expr = pat_data[0]

    matches = len(list(re.finditer(expr, sequence)))

    return matches


if __name__ == "__main__":
    exit(run_approx_raw(init_regexp, regexp, "regexp", argv))
