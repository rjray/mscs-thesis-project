# This is the runner module for the Python experiments. It provides the
# following importable functions:
#
#   * run() - Run one single-pattern, exact-matching experiment
#   * run_multi() - Run one multi-pattern, exact-matching experiment
#   * run_approx() - Run one single-pattern, approximate-matching experiment
#   * run_approx_raw() - Run one single-pattern, approximate-matching
#                        experiment without the usual pre-processing of the
#                        pattern and sequence data

from input import read_sequences, read_patterns, read_answers
from sys import stderr
from time import perf_counter


# Run a single-pattern, exact-matching experiment. Takes the init function
# pointer, the algorithm function pointer, the algorithm name (for reporting),
# and the arguments passed to the script.
def run(init, code, name, argv):
    if len(argv) < 3 or len(argv) > 4:
        raise Exception(f"Usage: {argv[0]} sequences patterns <answers>")

    sequences_data = read_sequences(argv[1])
    patterns_data = read_patterns(argv[2])
    if len(argv) == 4:
        answers_data = read_answers(argv[3])
        if len(answers_data) != len(patterns_data):
            raise Exception(
                "Count mismatch between patterns file and answers file"
            )
    else:
        answers_data = None

    start_time = perf_counter()
    return_code = 0

    # Preprocess patterns and sequences, since all of the algorithms that use
    # this module need (or can use) the same style of data.
    patterns_data = [list(map(ord, pattern)) for pattern in patterns_data]
    sequences_data = [list(map(ord, sequence)) for sequence in sequences_data]

    for pattern, pat in enumerate(patterns_data):
        pat_data = init(pat)

        for sequence, seq in enumerate(sequences_data):
            matches = code(pat_data, seq)

            if answers_data is not None:
                if matches != answers_data[pattern][sequence]:
                    print(
                        f"Pattern {pattern + 1} mismatch against sequence",
                        f"{sequence + 1} ({matches} !=",
                        f"{answers_data[pattern][sequence]})",
                        file=stderr
                    )
                    return_code += 1

    # Note the end-time before doing anything else:
    elapsed = perf_counter() - start_time

    print(f"language: python\nalgorithm: {name}\nruntime: {elapsed:.6f}")

    return return_code


# Run a multi-pattern, exact-matching experiment. Takes the init function
# pointer, the algorithm function pointer, the algorithm name (for reporting),
# and the arguments passed to the script.
def run_multi(init, code, name, argv):
    if len(argv) < 3 or len(argv) > 4:
        raise Exception(f"Usage: {argv[0]} sequences patterns <answers>")

    sequences_data = read_sequences(argv[1])
    patterns_data = read_patterns(argv[2])
    if len(argv) == 4:
        answers_data = read_answers(argv[3])
        if len(answers_data) != len(patterns_data):
            raise Exception(
                "Count mismatch between patterns file and answers file"
            )
    else:
        answers_data = None

    start_time = perf_counter()
    return_code = 0

    # Preprocess patterns and sequences, since all of the algorithms that use
    # this module need (or can use) the same style of data.
    patterns_data = [list(map(ord, pattern)) for pattern in patterns_data]
    sequences_data = [list(map(ord, sequence)) for sequence in sequences_data]
    pat_count = len(patterns_data)

    pat_data = init(patterns_data)

    for sequence, seq in enumerate(sequences_data):
        matches = code(pat_data, seq)

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

    print(f"language: python\nalgorithm: {name}\nruntime: {elapsed:.6f}")

    return return_code


# Run a single-pattern, approximate-matching experiment. Takes the same
# arguments as the previous two, with one optional argument that tells whether
# the data gets pre-processed. This is because the regular expression variant
# does not need the data pre-processed.
def run_approx_main(init, code, name, argv, preprocess=True):
    if len(argv) < 4 or len(argv) > 5:
        raise Exception(f"Usage: {argv[0]} k sequences patterns <answers>")

    k = int(argv[1])
    sequences_data = read_sequences(argv[2])
    patterns_data = read_patterns(argv[3])
    if len(argv) == 5:
        answers_file = argv[4] % k
        answers_data, k_read = read_answers(answers_file, True)
        if len(answers_data) != len(patterns_data):
            raise Exception(
                "Count mismatch between patterns file and answers file"
            )
        if k != k_read:
            raise Exception("Mismatch between k value and answers file")
    else:
        answers_data = None

    start_time = perf_counter()
    return_code = 0

    if preprocess:
        # Preprocess patterns and sequences, since most of the algorithms that
        # use this module need (or can use) the same style of data.
        patterns_data = [list(map(ord, pattern)) for pattern in patterns_data]
        sequences_data = [list(map(ord, sequence))
                          for sequence in sequences_data]

    for pattern, pat in enumerate(patterns_data):
        pat_data = init(pat, k)

        for sequence, seq in enumerate(sequences_data):
            matches = code(pat_data, seq)

            if answers_data is not None:
                if matches != answers_data[pattern][sequence]:
                    print(
                        f"Pattern {pattern + 1} mismatch against sequence",
                        f"{sequence + 1} ({matches} !=",
                        f"{answers_data[pattern][sequence]})",
                        file=stderr
                    )
                    return_code += 1

    # Note the end-time before doing anything else:
    elapsed = perf_counter() - start_time

    print(
        f"language: python\nalgorithm: {name}({k})\nruntime: {elapsed:.6f}"
    )

    return return_code


# Front-end to the previous function that runs *with* pre-processing.
def run_approx(init, code, name, argv):
    return run_approx_main(init, code, name, argv)


# Front-end to `run_approx_main` that runs *without* pre-processing.
def run_approx_raw(init, code, name, argv):
    return run_approx_main(init, code, name, argv, False)
