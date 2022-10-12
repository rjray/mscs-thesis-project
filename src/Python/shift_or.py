#!/usr/bin/env python3

from run import run
from sys import argv

ASIZE = 128
WORD = 64
MASK = 2 ** WORD - 1


def calc_s_positions(pat, m, s_positions):
    i = 0
    j = 1
    lim = 0

    while i < m:
        s_positions[pat[i]] &= (~j & MASK)
        lim |= j & MASK

        i += 1
        j <<= 1

    lim = ~(lim >> 1) & MASK

    return lim


def init_shift_or(pattern, m):
    if m > WORD:
        raise Exception(f"shift_or: pattern size my be <= {WORD}")

    s_positions = [~0 & MASK] * ASIZE
    lim = calc_s_positions(pattern, m, s_positions)

    return [pattern, lim, s_positions]


def shift_or(pat_data, m, seq, n):
    _, lim, s_positions = pat_data
    matches = 0

    state = ~0 & MASK
    for j in range(n):
        state = (state << 1 & MASK) | s_positions[seq[j]]
        if state < lim:
            matches += 1

    return matches


if __name__ == "__main__":
    exit(run(init_shift_or, shift_or, "shift_or", argv))
