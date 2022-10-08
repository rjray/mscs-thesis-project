#!/usr/bin/env python3

# Process the results from running the full test harness.

import argparse
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
from statistics import mean, median, stdev, variance
import yaml

NUMERICAL_KEYS = [
    "runtime", "total_runtime", "package", "pp0", "dram", "max_memory"
]
ALGORITHMS = ["kmp", "boyer_moore", "shift_or", "aho_corasick"]
ALGORITHM_LABELS = {
    "kmp": "Knuth-Morris-Pratt",
    "boyer_moore": "Boyer-Moore",
    "shift_or": "Shift-Or",
    "aho_corasick": "Aho-Corasick",
}
LANGUAGES = ["c-gcc", "c-llvm", "cpp-gcc", "cpp-llvm", "rust"]
LANGUAGE_LABELS = {
    "c-gcc": "C (GCC)",
    "c-llvm": "C (LLVM)",
    "cpp-gcc": "C++ (GCC)",
    "cpp-llvm": "C++ (LLVM)",
    "rust": "Rust",
}

DEFAULT_DATA_FILE = "experiments_data.yml"
DEFAULT_RUNTIMES_GRAPH = "runtimes.png"
DEFAULT_MEMORY_GRAPH = "memory.png"
DEFAULT_POWER_GRAPH = "power.png"
DEFAULT_PPS_GRAPH = "power_per_sec.png"
DEFAULT_TABLES_FILE = "latex-tables.tex"

SIMPLE_GRAPH_PARAMS = {
    "runtime": [
        "runtime", "Seconds", "Run-Time Comparison by Algorithm", "upper right"
    ],
    "memory": [
        "max_memory", "Megabytes", "Memory Usage by Algorithm", "lower right"
    ],
}

# Tracker for the number of tables written:
tables_written = 0


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
        "-m",
        "--memory",
        type=str,
        default=DEFAULT_MEMORY_GRAPH,
        help="File to write the memory graph to"
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
        "-t",
        "--tables",
        type=str,
        default=DEFAULT_TABLES_FILE,
        help="File to write the LaTeX tables into"
    )
    parser.add_argument(
        "-n",
        "--no-plots",
        action="store_true",
        help="Suppress generation of plots"
    )
    parser.add_argument(
        "-N",
        "--no-tables",
        action="store_true",
        help="Suppress generation of tables"
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
                if size != max_size:
                    # It can only be smaller
                    cell["notes"] = f"Based on {size} (of {max_size}) samples"
                new_data[lang][algo][key] = cell

    return new_data


# Create a bar graph for run-times or memory usage by algorithm.
def simple_graph(which, data, filename):
    if which not in SIMPLE_GRAPH_PARAMS:
        print(f"  Unknown graph type: {which}")
        return

    key, ylabel, title, legend = SIMPLE_GRAPH_PARAMS[which]

    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(LANGUAGES)
    steps = list(map(lambda x: x * step, range(len(LANGUAGES))))
    x_len = len(ALGORITHMS)
    x = np.arange(x_len)

    bars = {}
    for lang in LANGUAGES:
        bars[lang] = np.zeros(x_len, dtype=float)
        for idx, algo in enumerate(ALGORITHMS):
            bars[lang][idx] = data[lang][algo][key]["mean"]

    fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=300.0)
    for idx, lang in enumerate(LANGUAGES):
        ax.bar(x + steps[idx], bars[lang],
               step, label=LANGUAGE_LABELS[lang])

    ax.set_xticks(x + step * 2, map(lambda a: ALGORITHM_LABELS[a], ALGORITHMS))
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc=legend)

    fig.tight_layout()
    print(f"  Writing {filename}")
    fig.savefig(filename)

    return


# Create a stacked bar graph for energy used by algorithm.
def power_graph(data, filename, average=False):
    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(LANGUAGES)
    steps = list(map(lambda x: x * step, range(len(LANGUAGES))))
    x_len = len(ALGORITHMS)
    x = np.arange(x_len)

    runtimes = {}
    for lang in LANGUAGES:
        runtimes[lang] = np.array(
            [data[lang][algo]["total_runtime"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )

    pp0 = {}
    for lang in LANGUAGES:
        pp0[lang] = np.array(
            [data[lang][algo]["pp0"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )

    package = {}
    for lang in LANGUAGES:
        package[lang] = np.array(
            [data[lang][algo]["package"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )
        package[lang] -= pp0[lang]

    if average:
        for lang in LANGUAGES:
            pp0[lang] /= runtimes[lang]
            package[lang] /= runtimes[lang]

    fig, ax = plt.subplots()
    for idx, lang in enumerate(LANGUAGES):
        ax.bar(x + steps[idx], pp0[lang], step,
               label=f"{LANGUAGE_LABELS[lang]}")
        ax.bar(x + steps[idx], package[lang], step, bottom=pp0[lang])

    ax.set_xticks(x + step * 2, map(lambda a: ALGORITHM_LABELS[a], ALGORITHMS))
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


# Create a single table whose content is computed from the `data` parameter and
# write the LaTeX code to the open file `f`.
def create_computed_table(
    f, data, langs, algos, fields, *, axis="algorithms", caption=None,
    label=None
):
    global tables_written

    tables_written += 1

    if type(langs) != list:
        langs = [langs]
    if type(algos) != list:
        algos = [algos]
    if type(fields) != list:
        fields = [fields]

    algo_labels = list(map(lambda a: ALGORITHM_LABELS[a], algos))
    lang_labels = list(map(lambda l: LANGUAGE_LABELS[l], langs))

    if axis == "algorithms":
        width = len(algos)
        x_axis = algos
        x_labels = algo_labels
        height = len(langs)
        y_axis = langs
        y_labels = lang_labels
        headers = ["Language"]
    else:
        width = len(langs)
        x_axis = langs
        x_labels = lang_labels
        height = len(algos)
        y_axis = algos
        y_labels = algo_labels
        headers = ["Algorithm"]

    colspec = ["l"]
    for i in range(width):
        colspec.append("r")
        headers.append(x_labels[i])
    colspec = "|".join(colspec)
    headers = "&".join(headers)

    # Create the table of numbers
    table_data = np.zeros((height, width))
    for y_idx, y_str in enumerate(y_axis):
        for x_idx, x_str in enumerate(x_axis):
            if axis == "algorithms":
                table_data[y_idx][x_idx] = \
                    sum([data[y_str][x_str][key]["mean"] for key in fields])
            else:
                table_data[y_idx][x_idx] = \
                    sum([data[x_str][y_str][key]["mean"] for key in fields])
    # Normalize:
    table_data /= table_data.min()
    # Figure out where the 1.0 is:
    col = np.where(table_data == 1.0)
    col = col[1][0]

    # Now we need a map of the order to display rows in. We have to sort by the
    # values in the column that holds the 1.0, but not sort table_data itself.
    row_map = list(range(height))
    row_map.sort(key=lambda i: table_data[i][col])

    # Emit a newline before all subsequent tables:
    if tables_written > 1:
        print("", file=f)

    # Emit the preamble:
    print(f"%% Table #{tables_written}:", file=f)
    print(f"%% Language(s): {langs}", file=f)
    print(f"%% Algorithm(s): {algos}", file=f)
    print(f"%% Field(s): {fields}", file=f)
    print(f"%% Caption: {caption}", file=f)
    print(f"%% Label: {label}", file=f)
    print("\\begin{table}", file=f)
    print(f"\\begin{{tabular}}{{|{colspec}|}}", file=f)
    print("\\hline", file=f)
    print(f"{headers}\\\\", file=f)
    print("\\hline", file=f)

    for y_idx in row_map:
        row = [y_labels[y_idx]]
        for x_idx in range(width):
            row.append(f"{table_data[y_idx][x_idx]:.4f}")
        print("&".join(row) + "\\\\", file=f)

    print("\\hline", file=f)
    print("\\end{tabular}", file=f)
    if caption:
        print(f"\\caption{{{caption}}}", file=f)
    if label:
        print(f"\\label{{table:{label}}}", file=f)
    print("\\end{table}", file=f)

    return


# Create all the tables, using `data` and the `filename` given.
def create_tables(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        # Create each table individually.

        # Create a run-time table for each algorithm:
        for algo in ALGORITHMS:
            create_computed_table(
                f, data, LANGUAGES, algo, "runtime",
                caption=f"{ALGORITHM_LABELS[algo]} run-times",
                label=f"{algo}:runtime"
            )

        # Create a pp0/dram energy-usage table for each algorithm:
        for algo in ALGORITHMS:
            create_computed_table(
                f, data, LANGUAGES, algo, ["pp0", "dram"],
                caption=f"{ALGORITHM_LABELS[algo]} PP0/DRAM energy usage",
                label=f"{algo}:energy"
            )

        # Create a package energy-usage table for each algorithm:
        for algo in ALGORITHMS:
            create_computed_table(
                f, data, LANGUAGES, algo, "package",
                caption=f"{ALGORITHM_LABELS[algo]} package energy usage",
                label=f"{algo}:energy"
            )

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
        simple_graph("runtime", analyzed, args.runtimes)
        print("  Done.")
        print("\nCreating memory-usage graph...")
        simple_graph("memory", analyzed, args.memory)
        print("  Done.")
        print("\nCreating power usage graph...")
        power_graph(analyzed, args.power)
        print("  Done.")
        print("\nCreating power-per-second usage graph...")
        power_graph(analyzed, args.power_per_sec, True)
        print("  Done.")

    if not args.no_tables:
        print("\nCreating tables...")
        create_tables(analyzed, args.tables)

    print("\nDone.")

    return


if __name__ == "__main__":
    main()
