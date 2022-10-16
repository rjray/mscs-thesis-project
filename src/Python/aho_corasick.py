#!/usr/bin/env python3

from collections import deque
from run import run_multi
from sys import argv

ASIZE = 128
FAIL = -1
ALPHA_OFFSETS = [65, 67, 71, 84]
# This global is used only by enter_pattern() to track the index of new states
# as they're added to the goto_fn and output_fn arrays.
new_state = 0


def add_goto_state(goto_fn):
    goto_fn.append([FAIL] * ASIZE)


def enter_pattern(pat, idx, goto_fn, output_fn):
    length = len(pat)
    j = 0
    state = 0
    global new_state

    while goto_fn[state][pat[j]] != FAIL:
        state = goto_fn[state][pat[j]]
        j += 1
        if j == length:
            break

    for p in range(j, length):
        new_state += 1
        goto_fn[state][pat[p]] = new_state
        add_goto_state(goto_fn)
        output_fn.append(set())
        state = new_state

    output_fn[state].add(idx)

    return


def build_goto(patterns, goto_fn, output_fn):
    # Add initial values for state 0:
    add_goto_state(goto_fn)
    output_fn.append(set())

    # Add each pattern in turn:
    for idx, pattern in enumerate(patterns):
        enter_pattern(pattern, idx, goto_fn, output_fn)

    # Set unused transitions in state 0 to point to state 0:
    for i in range(ASIZE):
        if goto_fn[0][i] == FAIL:
            goto_fn[0][i] = 0

    return


def build_failure(goto_fn, output_fn):
    queue = deque()

    # The failure function should be the same length as goto_fn.
    failure_fn = [None] * len(goto_fn)

    # The queue starts out empty. Set it to be all states reachable from state
    # 0 and set failure(state) for those states to be 0.
    for i in ALPHA_OFFSETS:
        state = goto_fn[0][i]
        if state == 0:
            continue

        queue.append(state)
        failure_fn[state] = 0

    # This uses some single-letter variable names that match the published
    # algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
    # names.
    while queue:
        r = queue.popleft()
        for a in ALPHA_OFFSETS:
            s = goto_fn[r][a]
            if s == FAIL:
                continue

            queue.append(s)
            state = failure_fn[r]
            while goto_fn[state][a] == FAIL:
                state = failure_fn[state]
            failure_fn[s] = goto_fn[state][a]
            output_fn[s] |= output_fn[failure_fn[s]]

    return failure_fn


def init_aho_corasick(patterns_data):
    goto_fn = []
    output_fn = []
    build_goto(patterns_data, goto_fn, output_fn)
    failure_fn = build_failure(goto_fn, output_fn)
    pat_count = len(patterns_data)

    return [pat_count, goto_fn, failure_fn, output_fn]


# Perform the Aho-Corasick algorithm against the given sequence. No pattern is
# passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
# patterns in a single pass.
#
# Instead of returning a single int, returns an array of ints as long as the
# number of patterns (pattern_count).
def aho_corasick(pat_data, sequence):
    pattern_count, goto_fn, failure_fn, output_fn = pat_data

    matches = [0] * pattern_count
    state = 0

    for s in sequence:
        while goto_fn[state][s] == FAIL:
            state = failure_fn[state]

        state = goto_fn[state][s]
        for idx in output_fn[state]:
            matches[idx] += 1

    return matches


if __name__ == "__main__":
    exit(run_multi(init_aho_corasick, aho_corasick, "aho_corasick", argv))
