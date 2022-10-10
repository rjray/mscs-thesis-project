from setup import read_sequences, read_patterns, read_answers
from sys import stderr
from time import perf_counter


def run(code, name, argv):
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

    for sequence in range(len(sequences_data)):
        sequence_str = sequences_data[sequence]
        seq_len = len(sequence_str)

        for pattern in range(len(patterns_data)):
            pattern_str = patterns_data[pattern]
            pat_len = len(pattern_str)
            matches = code(pattern_str, pat_len, sequence_str, seq_len)

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
