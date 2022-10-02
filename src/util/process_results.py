#!/usr/bin/env python3

# Process the results from running the full test harness.

import argparse
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
from statistics import mean, median, stdev, variance
import yaml

NUMERICAL_KEYS = ["runtime", "package", "cpu", "oncoregpu", "dram", "psys"]


# Grab command-line arguments for the script.
def parse_command_line():
    parser = argparse.ArgumentParser()

    # Set up the arguments
    parser.add_argument(
        "input", nargs="?", default="experiments_data.yml",
        help="Input YAML data to process"
    )

    return parser.parse_args()


# Validate the data. Data validation here means:
#
#   1. No iterations of any language/algorithm pair failed
#   2. No successful iteration has a negative number for any of the power
#      readings
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
                print(
                    f"  ! Iteration {iteration} of {language} {algorithm}",
                    f"has a negative numerical value in {key}"
                )
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
            struct[language][algorithm].sort(key=itemgetter("iteration"))

    return struct, languages, algorithms


# Get the maximum size of any of the cells in data.
def get_max_size(data, langs, algos):
    sizes = []

    for lang in langs:
        for algo in algos:
            sizes.append(len(data[lang][algo]))

    return max(sizes)


# Do the analysis over the data. Determine means, medians, etc.
def analyze_data(data, langs, algos):
    # Start by getting the maximum size of iterations in the data. Everything
    # else will be held to this as the standard, and notes will be made on any
    # that are short.
    max_size = get_max_size(data, langs, algos)
    new_data = {}

    for lang in langs:
        if lang not in new_data:
            new_data[lang] = {}

        for algo in algos:
            if algo not in new_data[lang]:
                new_data[lang][algo] = {}

            iters = data[lang][algo]
            # For all of the numeric keys, gather the following:
            #
            #   1. Number of samples
            #   2. Mean
            #   3. Median
            #   4. Any notes about short samples
            for key in NUMERICAL_KEYS:
                cell = {"notes": None}
                values = map(lambda x: x[key], iters)
                values = list(filter(lambda x: x >= 0.0, values))
                size = len(values)
                cell["samples"] = size
                cell["mean"] = mean(values)
                cell["median"] = median(values)
                cell["stdev"] = stdev(values)
                cell["variance"] = variance(values)
                if size != max_size:
                    # It can only be smaller
                    cell["notes"] = f"Based on {size} samples"
                new_data[lang][algo][key] = cell

    return new_data


# Create a bar graph for run-times by algorithm.
def runtimes_graph(data):
    algorithms = ["kmp", "boyer_moore", "shift_or", "aho_corasick"]
    algo_labels = ["Knuth-Morris-Pratt",
                   "Boyer-Moore", "Shift Or", "Aho-Corasick"]
    languages = ["c-gcc", "c-llvm", "cpp-gcc", "cpp-llvm", "rust"]
    lang_labels = ["C (GCC)", "C (LLVM)", "C++ (GCC)", "C++ (LLVM)", "Rust"]

    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    steps = list(map(lambda x: x * step, range(len(languages))))
    x = np.arange(len(algorithms))

    bars = {}
    for lang in languages:
        bars[lang] = []
        for algo in algorithms:
            bars[lang].append(data[lang][algo]["runtime"]["mean"])

    fig, ax = plt.subplots()
    rects = []
    for idx, lang in enumerate(languages):
        rects.append(ax.bar(x + steps[idx], bars[lang],
                            step, label=lang_labels[idx]))

    ax.set_xticks(x + step * 2, algo_labels)
    ax.set_ylabel("Seconds")
    ax.set_title("Run-Time Comparison by Algorithm")
    ax.legend()

    fig.tight_layout()
    plt.show()


# Main loop. Read the data, validate it, turn it into useful structure.
def main():
    args = parse_command_line()

    print(f"Reading data from {args.input}...")
    data = []
    with open(args.input, "r") as file:
        for record in yaml.safe_load_all(file):
            data.append(record)
    print(f"  {len(data)} experiment records read.")

    print("Validating data...")
    if not validate(data):
        print("  Validation failed.")
        exit(1)
    print("  Data valid.")

    print("Building structure...")
    struct, languages, algorithms = build_structure(data)
    print("  Done.")
    print(f"\nLanguages detected: {languages}")
    print(f"\nAlgorithms detected: {algorithms}")

    print("\nAnalysis of data...")
    analyzed = analyze_data(struct, languages, algorithms)
    print("  Done.")
    # import pprint
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(analyzed)
    runtimes_graph(analyzed)

    return


if __name__ == "__main__":
    main()
