from input import read_sequences, read_patterns, read_answers
from sys import stderr
from time import perf_counter


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
