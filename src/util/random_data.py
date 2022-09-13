#!/usr/bin/env python

# Generate random data for the string matching experiments. Data should be
# drawn from the DNA alphabet, so as to simulate applying these techniques to
# DNA sequences.

import argparse
from math import ceil
import random


DEFAULT_SEQUENCES_FILE = "sequences.txt"
DEFAULT_PATTERNS_FILE = "patterns.txt"
ALPHABET = ["A", "C", "G", "T"]


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
        "--file",
        type=str,
        default=DEFAULT_SEQUENCES_FILE,
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
        "-c",
        "--count",
        type=int,
        default=100000,
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
        "--length",
        type=int,
        default=1024,
        help="Length of each sequence",
    )
    parser.add_argument(
        "-pl",
        "--pattern-length",
        type=int,
        default=10,
        dest="plength",
        help="Length of each pattern",
    )
    parser.add_argument(
        "-v",
        "--line-variance",
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


def write_sequences(*, file, count, length, line_variance, **_):
    print(f"\nCreating {count} sequences of length ", end="")
    print(f"{length} ± {line_variance}...", end="")
    sequences = []

    with open(file, "w", newline="\n") as f:
        for _ in range(count):
            sequence = create_sequence(length, line_variance)
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

        matched = 0
        for sequence in sequences:
            if pattern in sequence:
                matched += 1

    return pattern, matched / len(sequences)


def write_patterns(sequences, pfile, pcount, plength, pvariance, **_):
    print(f"\nGenerating {pcount} patterns of length ", end="")
    print(f"{plength} ± {pvariance}...\n")
    patterns = []
    avg_pct = 0.0
    # Current (hard-coded) threshold is 0.10% matching.
    threshold = ceil(len(sequences) / 1000)

    with open(pfile, "w", newline="\n") as f:
        for idx in range(pcount):
            print(f"    {idx+1}/{pcount}: ", end="")
            place = idx / pcount
            length = plength + \
                (random.randrange(0, 2 * pvariance + 1) - pvariance)

            while True:
                pattern, pct = create_pattern(
                    place, length, sequences, threshold
                )
                if pattern not in patterns:
                    break

            f.write(pattern + "\n")
            patterns.append(pattern)
            print(f"{(pct * 100):.2f}% matching.")
            avg_pct += pct

    avg_pct /= pcount
    print(f"\nAverage matching: {(avg_pct * 100):.2f}.")


def main():
    args = parse_command_line()

    print("Started.")

    # Apply a specific seed if given:
    if args["seed"] is not None:
        print(f"\n  Running with seed={args['seed']}")
        random.seed(args["seed"])

    sequences = write_sequences(**args)
    write_patterns(sequences=sequences, **args)

    print("\nDone.")


if __name__ == "__main__":
    main()
