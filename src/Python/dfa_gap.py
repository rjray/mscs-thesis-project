#!/usr/bin/env python3

from run import run_approx
from sys import argv

# Rather than do any contortions to limit the alphabet to just 4 characters,
# define it to be the ASCII range.
ASIZE = 128
FAIL = -1
# This list is used to keep some loops down to just the characters we're
# interested in.
ALPHABET = [65, 67, 71, 84]


# Create the DFA that underlies the DFA-Gap algorithm, based on the pattern,
# its length, and the parameter `k`.
def create_dfa(pattern, m, k):
    # We know that the number of states will be 1 + m + k(m - 1).
    max_states = 1 + m + k * (m - 1)

    # Allocate for the DFA
    dfa = [[FAIL] * ASIZE for _ in range(max_states)]

    # Start building the DFA. Start with state 0 and iterate through the
    # characters of `pattern`.

    # First step: Set d(0, p_0) = state(1)
    dfa[0][pattern[0]] = 1

    # Start `state` and `new_state` both at 1
    state = 1
    new_state = 1

    # Loop over remaining `pattern` (index 1 to the end). Because we know the
    # size of the DFA, there is no need to initialize each new state, that's
    # been done already.
    for char in pattern[1:]:
        new_state += 1
        dfa[state][char] = new_state
        last_state = state
        for j in range(1, k + 1):
            # For each of 1..k, we start a new state for which `char` maps to
            # `new_state`.
            dfa[new_state + j][char] = new_state
            for n in ALPHABET:
                if n != char:
                    dfa[last_state][n] = new_state + j
            last_state = new_state + j
        state = new_state
        new_state += k

    terminal = state

    return dfa, terminal


# Initialize the algorithm for the given `pattern` and value of `k`. Return a
# list that will be passed to `dfa_gap` with each target sequence to be
# matched in.
def init_dfa_gap(pattern, k):
    m = len(pattern)
    dfa, terminal = create_dfa(pattern, m, k)

    return [dfa, terminal, m]


# Apply the DFA-Gap algorithm to the given `sequence`, using the pattern data
# packed into `pat_data`.
def dfa_gap(pat_data, sequence):
    dfa, terminal, m = pat_data

    matches = 0
    n = len(sequence)

    end = n - m
    for i in range(end + 1):
        state = 0
        ch = 0

        while (i + ch) < n and dfa[state][sequence[i + ch]] != FAIL:
            state = dfa[state][sequence[i + ch]]
            ch += 1

        if state == terminal:
            matches += 1

    return matches


if __name__ == "__main__":
    exit(run_approx(init_dfa_gap, dfa_gap, "dfa_gap", argv))
