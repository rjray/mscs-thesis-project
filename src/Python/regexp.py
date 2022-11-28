#!/usr/bin/env python3

# Python implementation of the regular expression variant of DFA-Gap.

import re
from run import run_approx_raw
from sys import argv


# Initialize the algorithm for this pattern. Here, that means constructing the
# regular expression and returning it as the pattern data that will get passed
# to the primary routine for each sequence being matched against.
def init_regexp(pattern, k):
    # Create the regular expression for this pattern
    regexp = pattern[0]
    for char in pattern[1:]:
        regexp += f"[^{char}]{{0,{k}}}{char}"
    regexp = f"(?=({regexp}))"

    return [regexp]


# Run the regular expression variant on the given `sequence`, using the regexp
# pattern in `pat_data`.
def regexp(pat_data, sequence):
    expr = pat_data[0]

    # Yes, it's this short in Python:
    matches = len(list(re.findall(expr, sequence)))

    return matches


if __name__ == "__main__":
    exit(run_approx_raw(init_regexp, regexp, "regexp", argv))
