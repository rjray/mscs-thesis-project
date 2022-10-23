#!/usr/bin/env python3

# Generate random data for the string matching experiments. Data should be
# drawn from the DNA alphabet, so as to simulate applying these techniques to
# DNA sequences.

import argparse
from math import ceil
import random
import re
from statistics import mean
from sys import stdout


DEFAULT_SEQUENCES_FILE = "sequences.txt"
DEFAULT_PATTERNS_FILE = "patterns.txt"
DEFAULT_ANSWERS_FILE = "answers.txt"
DEFAULT_APPROX_ANSWERS_FILE = "answers-k-%d.txt"

ALPHABET = ["A", "C", "G", "T"]
ALPHABET_SET = set(ALPHABET)


def parse_command_line():
    parser = argparse.ArgumentParser()

    # Set up the arguments
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        help="Random seed to use in data generation",
    )
    parser.add_argument(
        "-f",
        "--sequences",
        type=str,
        default=DEFAULT_SEQUENCES_FILE,
        dest="file",
        help="Name of file to write sequence data to",
    )
    parser.add_argument(
        "-p",
        "--patterns",
        type=str,
        default=DEFAULT_PATTERNS_FILE,
        dest="pfile",
        help="Name of file to write pattern data to",
    )
    parser.add_argument(
        "-a",
        "--answers",
        type=str,
        default=DEFAULT_ANSWERS_FILE,
        dest="afile",
        help="Name of file to write answers data to",
    )
    parser.add_argument(
        "-A",
        "--approx-answers",
        type=str,
        default=DEFAULT_APPROX_ANSWERS_FILE,
        dest="amfile",
        help="Name of file to write answers data to",
    )
    parser.add_argument(
        "-c",
        "--sequence-count",
        type=int,
        default=100000,
        dest="count",
        help="Number of sequences to generate",
    )
    parser.add_argument(
        "-pc",
        "--pattern-count",
        type=int,
        default=100,
        dest="pcount",
        help="Number of patterns to generate",
    )
    parser.add_argument(
        "-l",
        "--sequence-length",
        type=int,
        default=1024,
        dest="length",
        help="Length of each sequence",
    )
    parser.add_argument(
        "-pl",
        "--pattern-length",
        type=int,
        default=9,
        dest="plength",
        help="Length of each pattern",
    )
    parser.add_argument(
        "-v",
        "--sequence-variance",
        type=int,
        default=0,
        help="Variance for sequence length",
    )
    parser.add_argument(
        "-pv",
        "--pattern-variance",
        type=int,
        default=0,
        dest="pvariance",
        help="Variance for pattern length",
    )
    parser.add_argument(
        "-k",
        type=str,
        help="Value(s) of k for approximate matching, comma-separated"
    )

    return vars(parser.parse_args())


def create_sequence(length, variance):
    # Build up the sequence as an array. Should be a little faster than
    # string concatenation.
    seq = []
    # Determine how many characters to generate, as (length ± variance)
    chars = length + (random.randrange(0, 2 * variance + 1) - variance)

    for _ in range(chars):
        seq.append(ALPHABET[random.randrange(0, 4)])

    return "".join(seq)


def write_sequences(*, file, count, length, sequence_variance, **_):
    print(f"\nCreating {count} sequences of length ", end="")
    print(f"{length} ± {sequence_variance}...", end="")
    stdout.flush()
    sequences = []

    with open(file, "w", newline="\n") as f:
        f.write(f"{count} {length + sequence_variance}\n")
        for _ in range(count):
            sequence = create_sequence(length, sequence_variance)
            f.write(sequence + "\n")
            sequences.append(sequence)

    print(" done.")
    return sequences


def create_pattern(place, length, sequences, threshold):
    source = sequences[int(place * len(sequences))]
    matched = 0

    while matched < threshold:
        base = random.randrange(0, len(source) - length)
        pattern = source[base:base + length]
        # Use this pattern if we want to find overlapping matches:
        re_pat = f"(?={pattern})"

        matched = 0
        matches = []
        for sequence in sequences:
            matches.append([m.start() for m in re.finditer(re_pat, sequence)])
            if len(matches[-1]):
                matched += 1

    return pattern, matched, matches


def write_patterns(sequences, afile, pfile, pcount, plength, pvariance, **_):
    print(f"\nGenerating {pcount} patterns of length ", end="")
    print(f"{plength} ± {pvariance}...\n")
    patterns = []
    all_pct = []
    # Current (hard-coded) threshold is 0.10% matching.
    count = len(sequences)
    threshold = ceil(count / 1000)

    with open(pfile, "w", newline="\n") as pf:
        pf.write(f"{pcount} {plength + pvariance}\n")
        with open(afile, "w", newline="\n") as af:
            af.write(f"{pcount} {count}\n")
            for idx in range(pcount):
                print(f"    Pattern {idx+1}/{pcount}: ", end="")
                stdout.flush()
                place = idx / pcount
                length = plength + \
                    (random.randrange(0, 2 * pvariance + 1) - pvariance)

                while True:
                    pattern, matched, matches = create_pattern(
                        place, length, sequences, threshold
                    )
                    if pattern not in patterns:
                        break

                pf.write(pattern + "\n")
                patterns.append(pattern)
                af.write(",".join(map(lambda x: str(len(x)), matches)) + "\n")
                pct = matched / count
                print(f"{(pct * 100):.2f}% matching ({matched}).")
                all_pct.append(pct)

    avg_pct = mean(all_pct)
    lo_pct = min(all_pct)
    hi_pct = max(all_pct)
    print(f"\nDone. Average matching: {(avg_pct * 100):.2f}% ", end="")
    print(f"(low={(lo_pct * 100):.2f}%, high={(hi_pct * 100):.2f}%)")

    return patterns


def write_approximate_answers(k, patterns, sequences, amfile):
    # The file to write the approximate-matching answers to, based on k:
    file = amfile % k
    with open(file, "w", newline="\n") as f:
        f.write(f"{len(patterns)} {len(sequences)} {k}\n")

        # Loop over patterns
        for pattern in patterns:
            # Create the regular expression for this pattern
            regexp = pattern[0]
            for char in pattern[1:]:
                regexp += "[%s]{0,%d}%s" % (
                    "".join(ALPHABET_SET - set(char)), k, char
                )
            regexp = f"(?={regexp})"

            matches = []
            # Loop over sequences
            for sequence in sequences:
                matches.append(
                    [m.start() for m in re.finditer(regexp, sequence)]
                )

            f.write(",".join(map(lambda x: str(len(x)), matches)) + "\n")

    return


def main():
    args = parse_command_line()

    print("Started.")

    # Apply a specific seed if given:
    if args["seed"] is not None:
        print(f"\n  Running with seed={args['seed']}")
        random.seed(args["seed"])

    sequences = write_sequences(**args)
    patterns = write_patterns(sequences=sequences, **args)
    if args["k"] is not None:
        print()
        ks = map(int, args["k"].split(","))
        for k in ks:
            print(f"Generating approximate matches for k={k}...", end="")
            stdout.flush()
            write_approximate_answers(k, patterns, sequences, args["amfile"])
            print(" done.")

    print("\nDone.")


if __name__ == "__main__":
    main()
