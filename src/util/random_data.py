#!/usr/bin/env python

# Generate random data for the string matching experiments. Data should be
# drawn from the DNA alphabet, so as to simulate applying these techniques to
# DNA sequences.

import argparse
import random


DEFAULT_DATA_FILE = "sequences.txt"
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
        default=DEFAULT_DATA_FILE,
        help="Name of file to write data to",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=100000,
        help="Number of sequences to generate",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=1024,
        help="Length of each sequence",
    )
    parser.add_argument(
        "-v",
        "--line-variance",
        type=int,
        default=0,
        help="Variance for sequence length",
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
    seq.append("\n")

    return "".join(seq)


def main():
    args = parse_command_line()

    # Apply a specific seed if given:
    if args["seed"] is not None:
        random.seed(args["seed"])

    with open(args["file"], "w", newline="\n") as f:
        for _ in range(args["count"]):
            f.write(create_sequence(args["length"], args["line_variance"]))


if __name__ == "__main__":
    main()
