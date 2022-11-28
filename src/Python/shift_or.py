#!/usr/bin/env python3

# The Python implementation of the Shift-Or (Bitap) algorithm.

from run import run
from sys import argv

# Rather than do any contortions to limit the alphabet to just 4 characters,
# define it to be the ASCII range.
ASIZE = 128
# Define the word size as 64 bits.
WORD = 64
# Because of how Python handles integers, it is necessary to mask most of the
# bit-wise operations to WORD bits in length. Note that this incurred quite a
# performance hit on this version.
MASK = 2 ** WORD - 1


# Calculate the S-positions array and compute the value of `lim`. Return both.
def calc_s_positions(pat, m):
    s_positions = [~0 & MASK] * ASIZE
    i = 0
    j = 1
    lim = 0

    while i < m:
        s_positions[pat[i]] &= (~j & MASK)
        lim |= j & MASK

        i += 1
        j <<= 1

    lim = ~(lim >> 1) & MASK

    return lim, s_positions


# Initialize the algorithm for the given pattern. Create the `s_positions` and
# `lim` values from `pattern` and return a list of them. Note that `pattern` is
# not needed for matching.
def init_shift_or(pattern):
    m = len(pattern)
    if m > WORD:
        raise Exception(f"shift_or: pattern size must be <= {WORD}")

    return calc_s_positions(pattern, m)


# Run the Shift-Or algorithm on the given sequence `seq`, using the pattern
# data in `pat_data`. Return the number of matches found.
def shift_or(pat_data, seq):
    lim, s_positions = pat_data
    matches = 0

    # Get size of sequence. Pattern size not needed here.
    n = len(seq)

    state = ~0 & MASK
    for j in range(n):
        state = (state << 1 & MASK) | s_positions[seq[j]]
        if state < lim:
            matches += 1

    return matches


if __name__ == "__main__":
    exit(run(init_shift_or, shift_or, "shift_or", argv))
