#!/usr/bin/env python3

# Python implementation of the Knuth-Morris-Pratt algorithm.

from copy import copy
from run import run
from sys import argv


# Calculate the `next_table` jump-table.
def make_next_table(pattern, m):
    i = 0
    next_table = [0 for _ in range(m + 1)]
    j = next_table[0] = -1

    while i < m:
        while j > -1 and pattern[i] != pattern[j]:
            j = next_table[j]

        i += 1
        j += 1
        if pattern[i] == pattern[j]:
            next_table[i] = next_table[j]
        else:
            next_table[i] = j

    return next_table


# Initialize the algorithm for the given pattern. Requires adding a sentinel
# character to the pattern and creating the `next_table` array. Return an
# array of the data that will be needed to use this for matching to sequences.
def init_kmp(pattern):
    m = len(pattern)
    pat = copy(pattern)
    pat.append(0)

    return [pat, make_next_table(pat, m)]


# Run the KMP algorithm over the given `sequence` using the pattern encoded in
# `pat_data`. Return the number of matches found.
def kmp(pat_data, sequence):
    pat, next_table = pat_data
    matches = 0

    # Get sizes of pat and sequence. Account for the sentinel value in pat.
    m = len(pat) - 1
    n = len(sequence)

    i, j = 0, 0

    while j < n:
        while i > -1 and pat[i] != sequence[j]:
            i = next_table[i]

        i += 1
        j += 1
        if i >= m:
            matches += 1
            i = next_table[i]

    return matches


if __name__ == "__main__":
    exit(run(init_kmp, kmp, "kmp", argv))
