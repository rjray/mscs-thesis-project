#!/usr/bin/env python3

from collections import deque
from setup import read_sequences, read_patterns, read_answers
from sys import argv, stderr
from time import perf_counter

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
        enter_pattern(list(map(ord, pattern)), idx, goto_fn, output_fn)

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


# Perform the Aho-Corasick algorithm against the given sequence. No pattern is
# passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
# patterns in a single pass.
#
# Instead of returning a single int, returns an array of ints as long as the
# number of patterns (pattern_count).
def aho_corasick(sequence, pattern_count, goto_fn, failure_fn, output_fn):
    matches = [0] * pattern_count
    state = 0

    for s in map(ord, sequence):
        while goto_fn[state][s] == FAIL:
            state = failure_fn[state]

        state = goto_fn[state][s]
        for idx in output_fn[state]:
            matches[idx] += 1

    return matches


# This is a customization of the runner function used for the single-pattern
# matching algorithms. This one sets up the structures needed for the A-C
# algorithm, then iterates over the sequences (since iterating over the
# patterns is not necessary).
#
# The return value is 0 if the experiment correctly identified all pattern
# instances in all sequences, and the number of misses otherwise.
def run(args):
    if len(args) < 3 or len(args) > 4:
        raise Exception(f"Usage: {args[0]} sequences patterns <answers>")

    sequences_data = read_sequences(args[1])
    patterns_data = read_patterns(args[2])
    if len(args) == 4:
        answers_data = read_answers(args[3])
        if len(answers_data) != len(patterns_data):
            raise Exception(
                "Count mismatch between patterns file and answers file"
            )
    else:
        answers_data = None

    start_time = perf_counter()
    return_code = 0

    goto_fn = []
    output_fn = []
    build_goto(patterns_data, goto_fn, output_fn)
    failure_fn = build_failure(goto_fn, output_fn)
    pat_count = len(patterns_data)

    for sequence, sequence_str in enumerate(sequences_data):
        matches = aho_corasick(
            sequence_str, pat_count, goto_fn, failure_fn, output_fn
        )

        if answers_data:
            for pattern in range(pat_count):
                if matches[pattern] != answers_data[pattern][sequence]:
                    print(
                        f"Pattern {pattern + 1} mismatch against sequence",
                        f"{sequence + 1} ({matches[pattern]} !=",
                        f"{answers_data[pattern][sequence]})",
                        file=stderr
                    )
                    return_code += 1

    # Note the end-time before doing anything else:
    elapsed = perf_counter() - start_time

    print(f"language: python\nalgorithm: aho_corasick\nruntime: {elapsed:.6f}")

    return return_code


if __name__ == "__main__":
    exit(run(argv))
