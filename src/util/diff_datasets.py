#!/usr/bin/env python3

# Derive some stats from 2+ full experiments runs, side-by-side.

import argparse
import numpy as np
from operator import itemgetter
from statistics import mean, median, stdev, variance
import yaml

NUMERICAL_KEYS = [
    "runtime", "total_runtime", "package", "pp0", "dram", "max_memory"
]

FIX_CONST = 2**32 * 0.00006104

ALGORITHMS = ["kmp", "boyer_moore", "shift_or", "aho_corasick"]
APPROX_ALGORITHMS = [f"dfa_gap({k + 1})" for k in range(5)]
APPROX_ALGORITHMS += [f"regexp({k + 1})" for k in range(5)]
ALL_ALGORITHMS = ALGORITHMS + APPROX_ALGORITHMS
ALGORITHM_LABELS = {
    "kmp": "Knuth-Morris-Pratt",
    "boyer_moore": "Boyer-Moore",
    "shift_or": "Bitap",
    "aho_corasick": "Aho-Corasick",
}
for k in range(5):
    ALGORITHM_LABELS[APPROX_ALGORITHMS[k]] = f"DFA-Gap (k={k + 1})"
    ALGORITHM_LABELS[APPROX_ALGORITHMS[k + 5]] = f"Regexp-Gap (k={k + 1})"

LANGUAGES = [
    "c-gcc", "c-llvm", "c-intel", "cpp-gcc", "cpp-llvm", "cpp-intel", "rust",
    "perl", "python"
]
LANGUAGE_LABELS = {
    "c-gcc": "C (GCC)",
    "c-llvm": "C (LLVM)",
    "c-intel": "C (Intel)",
    "cpp-gcc": "C++ (GCC)",
    "cpp-llvm": "C++ (LLVM)",
    "cpp-intel": "C++ (Intel)",
    "rust": "Rust",
    "perl": "Perl",
    "python": "Python",
}


# Grab command-line arguments for the script.
def parse_command_line():
    parser = argparse.ArgumentParser()

    # Set up the arguments
    parser.add_argument(
        "input",
        nargs="*",
        help="Input YAML data files to process"
    )

    return parser.parse_args()


# Validate the data. Data validation here means:
#
#   1. No iterations of any language/algorithm pair failed
#   2. Any iteration that has a negative value for any of the numerical keys
#      is adjusted back into range.
def validate(data):
    good = True

    for record in data:
        language = record["language"]
        algorithm = record["algorithm"]
        iteration = record["iteration"]

        if not record["success"]:
            print(f"  Iteration {iteration} of {language} {algorithm} failed")
            good = False
            continue

        for key in NUMERICAL_KEYS:
            if record[key] < 0.0:
                # Because the MSRs that are read for energy consumption numbers
                # roll over at 32 bits, sometimes we get a negative number that
                # stems from the "after" value being smaller than the "before".
                print(
                    f"  ! Iteration {iteration} of {language} {algorithm}",
                    f"has a negative numerical value in {key}"
                )
                fix_val = FIX_CONST + record[key]
                print(f"    Value {record[key]} corrected to {fix_val}")
                record[key] = fix_val
                continue

    return good


# Build the structured data. Data is indexed first by language, then by
# algorithm within language. At each of those places is an array of the
# iterations for that pair.
#
# Return a tuple of (data, languages, algorithms)
def build_structure(data):
    struct = {}
    languages = []
    algorithms = []

    for record in data:
        language = record["language"]
        algorithm = record["algorithm"]

        if language not in struct:
            struct[language] = {}
            languages.append(language)
        if algorithm not in struct[language]:
            struct[language][algorithm] = []
            if algorithm not in algorithms:
                algorithms.append(algorithm)

        struct[language][algorithm].append(record)

    for language in languages:
        for algorithm in algorithms:
            if algorithm in struct[language]:
                struct[language][algorithm].sort(key=itemgetter("iteration"))

    return struct, languages, algorithms


# Do the analysis over the data. Determine means, medians, etc.
def analyze_data(data, langs, algos):
    new_data = {}

    for lang in langs:
        if lang not in new_data:
            new_data[lang] = {}

        for algo in algos:
            if algo not in data[lang]:
                continue

            if algo not in new_data[lang]:
                new_data[lang][algo] = {}

            iters = data[lang][algo]
            # For all of the numeric keys, gather the following:
            #
            #   1. Number of samples
            #   2. Mean
            #   3. Median
            #   4. Standard deviation
            #   5. Variance
            #   6. Any notes about short samples
            for key in NUMERICAL_KEYS:
                cell = {}
                values = map(lambda x: x[key], iters)
                values = np.array(
                    list(filter(lambda x: x >= 0.0, values)), dtype=float
                )
                # Scale memory down to Mb:
                if key == "max_memory":
                    values /= 1024.0
                size = len(values)
                cell["samples"] = size
                cell["mean"] = mean(values)
                cell["median"] = median(values)
                cell["stdev"] = stdev(values)
                cell["variance"] = variance(values)
                new_data[lang][algo][key] = cell

    return new_data


def read_and_process(filename):
    print(f"\n  Reading experiments data from {filename}...")
    data = []
    with open(filename, "r") as file:
        for record in yaml.safe_load_all(file):
            data.append(record)
    print(f"    {len(data)} experiment records read.")

    print(f"  Validating {filename} data...")
    if not validate(data):
        print("    Validation failed.")
        exit(1)
    print("    Data valid.")

    print(f"  Building {filename} data structure...")
    struct, languages, algorithms = build_structure(data)
    print("    Done.")

    print(f"  Analysis of {filename} data...")
    analyzed = analyze_data(struct, languages, algorithms)
    print("    Done.")

    # Create the pseudo-matrix data structures to be returned:
    runtimes = []
    for lang in languages:
        runtimes.append(
            [analyzed[lang][a]["runtime"]["mean"] for a in algorithms]
        )

    energy = []
    for lang in languages:
        row = [0.] * len(algorithms)
        for i, a in enumerate(algorithms):
            row[i] = analyzed[lang][a]["package"]["mean"]
            row[i] += analyzed[lang][a]["dram"]["mean"]
        energy.append(row)

    return np.array(runtimes), np.array(energy)


def main():
    args = parse_command_line()
    if len(args.input) != 3:
        print("Need 3 files to process.")
        exit(1)

    data = []
    print(f"Processing {len(args.input)} files:")
    for filename in args.input:
        data.append(read_and_process(filename))

    runtimes = []
    energy = []
    for rt, en in data:
        runtimes.append(rt)
        energy.append(en)

    for a, b in [(0, 1), (1, 2)]:
        print()

        A = runtimes[a]
        B = runtimes[b]
        diff = (A - B) / A

        print(f"({a},{b}) runtimes min: {(diff.min() * 100):.4f}%")
        print(f"({a},{b}) runtimes max: {(diff.max() * 100):.4f}%")
        print(f"({a},{b}) runtimes avg: {(diff.mean() * 100):.4f}%")

        A = energy[a]
        B = energy[b]
        diff = (A - B) / A

        print(f"({a},{b}) energy min: {(diff.min() * 100):.4f}%")
        print(f"({a},{b}) energy max: {(diff.max() * 100):.4f}%")
        print(f"({a},{b}) energy avg: {(diff.mean() * 100):.4f}%")


if __name__ == "__main__":
    main()
