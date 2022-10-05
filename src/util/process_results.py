#!/usr/bin/env python3

# Process the results from running the full test harness.

import argparse
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
from statistics import mean, median, stdev, variance
import yaml

NUMERICAL_KEYS = ["runtime", "total_runtime", "package", "pp0", "dram"]
DEFAULT_DATA_FILE = "experiments_data.yml"
DEFAULT_RUNTIMES_GRAPH = "runtimes.png"
DEFAULT_POWER_GRAPH = "power.png"
DEFAULT_PPS_GRAPH = "power_per_sec.png"


# Grab command-line arguments for the script.
def parse_command_line():
    parser = argparse.ArgumentParser()

    # Set up the arguments
    parser.add_argument(
        "input", nargs="?", default=DEFAULT_DATA_FILE,
        help="Input YAML data to process"
    )
    parser.add_argument(
        "-r",
        "--runtimes",
        type=str,
        default=DEFAULT_RUNTIMES_GRAPH,
        help="File to write the run-times graph to"
    )
    parser.add_argument(
        "-p",
        "--power",
        type=str,
        default=DEFAULT_POWER_GRAPH,
        help="File to write the power usage graph to"
    )
    parser.add_argument(
        "-P",
        "--power-per-sec",
        type=str,
        default=DEFAULT_PPS_GRAPH,
        help="File to write the power-per-second usage graph to"
    )
    parser.add_argument(
        "-n",
        "--no-plots",
        action="store_true",
        help="Suppress generation of plots"
    )
    parser.add_argument(
        "-d",
        "--dump",
        action="store_true",
        help="Dump processed data"
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
            #   4. Standard deviation
            #   5. Variance
            #   6. Any notes about short samples
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
def runtimes_graph(data, filename):
    algorithms = ["kmp", "boyer_moore", "shift_or", "aho_corasick"]
    algo_labels = ["Knuth-Morris-Pratt",
                   "Boyer-Moore", "Shift Or", "Aho-Corasick"]
    languages = ["c-gcc", "c-llvm", "cpp-gcc", "cpp-llvm", "rust"]
    lang_labels = ["C (GCC)", "C (LLVM)", "C++ (GCC)", "C++ (LLVM)", "Rust"]

    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    steps = list(map(lambda x: x * step, range(len(languages))))
    x_len = len(algorithms)
    x = np.arange(x_len)

    bars = {}
    for lang in languages:
        bars[lang] = np.zeros(x_len, dtype=float)
        for idx, algo in enumerate(algorithms):
            bars[lang][idx] = data[lang][algo]["runtime"]["mean"]

    fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=300.0)
    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], bars[lang],
               step, label=lang_labels[idx])

    ax.set_xticks(x + step * 2, algo_labels)
    ax.set_ylabel("Seconds")
    ax.set_title("Run-Time Comparison by Algorithm")
    ax.legend()

    fig.tight_layout()
    print(f"  Writing {filename}")
    fig.savefig(filename)

    return


# Create a bar graph for run-times by algorithm.
def power_graph(data, filename, average=False):
    algorithms = ["kmp", "boyer_moore", "shift_or", "aho_corasick"]
    algo_labels = ["Knuth-Morris-Pratt",
                   "Boyer-Moore", "Shift Or", "Aho-Corasick"]
    languages = ["c-gcc", "c-llvm", "cpp-gcc", "cpp-llvm", "rust"]
    lang_labels = ["C (GCC)", "C (LLVM)", "C++ (GCC)", "C++ (LLVM)", "Rust"]

    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    steps = list(map(lambda x: x * step, range(len(languages))))
    x_len = len(algorithms)
    x = np.arange(x_len)

    runtimes = {}
    for lang in languages:
        runtimes[lang] = np.array(
            [data[lang][algo]["total_runtime"]["mean"] for algo in algorithms],
            dtype=float
        )

    pp0 = {}
    for lang in languages:
        pp0[lang] = np.array(
            [data[lang][algo]["pp0"]["mean"] for algo in algorithms],
            dtype=float
        )

    package = {}
    for lang in languages:
        package[lang] = np.array(
            [data[lang][algo]["package"]["mean"] for algo in algorithms],
            dtype=float
        )
        package[lang] -= pp0[lang]

    if average:
        for lang in languages:
            pp0[lang] /= runtimes[lang]
            package[lang] /= runtimes[lang]

    fig, ax = plt.subplots()
    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], pp0[lang], step,
               label=f"{lang_labels[idx]}")
        ax.bar(x + steps[idx], package[lang], step, bottom=pp0[lang])

    ax.set_xticks(x + step * 2, algo_labels)
    if average:
        ax.set_ylabel("Avg Joules per Second")
        ax.set_title("Total Energy Use (per second) Comparison by Algorithm")
    else:
        ax.set_ylabel("Joules")
        ax.set_title("Total Energy Use Comparison by Algorithm")
    if average:
        ax.legend(loc="lower right")
    else:
        ax.legend()

    fig.tight_layout()
    print(f"  Writing {filename}")
    fig.savefig(filename)

    return


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

    if args.dump:
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(analyzed)

    if not args.no_plots:
        print("\nCreating runtimes graph...")
        runtimes_graph(analyzed, args.runtimes)
        print("  Done.")

    if not args.no_plots:
        print("\nCreating power usage graph...")
        power_graph(analyzed, args.power)
        print("  Done.")

    if not args.no_plots:
        print("\nCreating power-per-second usage graph...")
        power_graph(analyzed, args.power_per_sec, True)
        print("  Done.")

    return


if __name__ == "__main__":
    main()
