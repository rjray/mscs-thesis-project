#!/usr/bin/env python3

from run import run
from sys import argv


def init_kmp(pattern, m, next_table):
    i = 0
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

    return


def kmp(pattern, m, sequence, n):
    pat = pattern + "\0"
    matches = 0
    next_table = [0 for _ in range(m + 1)]

    init_kmp(pat, m, next_table)
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
    exit(run(kmp, "kmp", argv))
