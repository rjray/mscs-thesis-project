#!/usr/bin/env python3

from copy import copy
from run import run
from sys import argv

ASIZE = 128


def calc_bad_char(pat, m):
    bad_char = [m] * ASIZE

    for i in range(m - 1):
        bad_char[pat[i]] = m - 1 - i

    return bad_char


def calc_suffixes(pat, m):
    suffix_list = [0] * m

    suffix_list[m - 1] = m

    f = 0
    g = m - 1
    for i in range(m - 2, -1, -1):
        if i > g and suffix_list[i + m - 1 - f] < i - g:
            suffix_list[i] = suffix_list[i + m - 1 - f]
        else:
            if i < g:
                g = i

            f = i
            while g >= 0 and pat[g] == pat[g + m - 1 - f]:
                g -= 1

            suffix_list[i] = f - g

    return suffix_list


def calc_good_suffix(pat, m):
    suffixes = calc_suffixes(pat, m)
    good_suffix = [m] * m

    j = 0
    i = m - 1
    while i >= -1:
        if i == -1 or suffixes[i] == i + 1:
            while j < m - 1 - i:
                if good_suffix[j] == m:
                    good_suffix[j] = m - 1 - i

                j += 1

        i -= 1

    for i in range(m - 1):
        good_suffix[m - 1 - suffixes[i]] = m - 1 - i

    return good_suffix


def init_boyer_moore(pattern):
    m = len(pattern)
    pat = copy(pattern)
    pat.append(0)

    return [pat, calc_good_suffix(pat, m), calc_bad_char(pat, m)]


def boyer_moore(pat_data, seq):
    pat, good_suffix, bad_char = pat_data
    matches = 0

    # Get sizes of pat and sequence. Account for the sentinel value in pat.
    m = len(pat) - 1
    n = len(seq)

    j = 0
    while j <= n - m:
        i = m - 1
        while i >= 0 and pat[i] == seq[i + j]:
            i -= 1
        if i < 0:
            matches += 1
            j += good_suffix[0]
        else:
            j += max(good_suffix[i], bad_char[seq[i + j]] - m + 1 + i)

    return matches


if __name__ == "__main__":
    exit(run(init_boyer_moore, boyer_moore, "boyer_moore", argv))
