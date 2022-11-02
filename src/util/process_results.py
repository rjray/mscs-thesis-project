#!/usr/bin/env python3

# Process the results from running the full test harness.

import argparse
import datetime
import matplotlib.pyplot as plt
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
SCRIPT_ONLY_ALGORITHMS = [f"regexp({k + 1})" for k in range(5)]
ALGORITHM_LABELS = {
    "kmp": "Knuth-Morris-Pratt",
    "boyer_moore": "Boyer-Moore",
    "shift_or": "Bitap",
    "aho_corasick": "Aho-Corasick",
    "combined": "Combined Data",
}
for k in range(5):
    ALGORITHM_LABELS[APPROX_ALGORITHMS[k]] = f"DFA-Gap (k={k + 1})"
    ALGORITHM_LABELS[SCRIPT_ONLY_ALGORITHMS[k]] = f"Regexp (k={k + 1})"

LANGUAGES = [
    "c-gcc", "c-llvm", "c-intel", "cpp-gcc", "cpp-llvm", "cpp-intel", "rust"
]
SCRIPT_LANGUAGES = ["perl", "python"]
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

DEFAULT_FILES = {
    "data": "experiments_data.yml",
    "runtimes_graph": "runtimes.png",
    "power_graph": "power.png",
    "pps_graph": "power_per_sec.png",
    "script_runtimes_graph": "runtimes-scripts.png",
    "script_power_graph": "power-scripts.png",
    "basic_tables_file": "latex-tables.tex",
    "iterations_table_file": "iterations.tex",
}

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
        "input", nargs="?", default=DEFAULT_FILES["data"],
        help="Input YAML data to process"
    )
    parser.add_argument(
        "--runtimes",
        type=str,
        default=DEFAULT_FILES["runtimes_graph"],
        help="File to write the run-times graph to"
    )
    parser.add_argument(
        "--script-runtimes",
        type=str,
        default=DEFAULT_FILES["script_runtimes_graph"],
        help="File to write the scripts run-times graph to"
    )
    parser.add_argument(
        "--power",
        type=str,
        default=DEFAULT_FILES["power_graph"],
        help="File to write the power usage graph to"
    )
    parser.add_argument(
        "--script-power",
        type=str,
        default=DEFAULT_FILES["script_power_graph"],
        help="File to write the scripts power usage graph to"
    )
    parser.add_argument(
        "--power-per-sec",
        type=str,
        default=DEFAULT_FILES["pps_graph"],
        help="File to write the power-per-second usage graph to"
    )
    parser.add_argument(
        "-t",
        "--basic-tables",
        type=str,
        default=DEFAULT_FILES["basic_tables_file"],
        help="File to write the basic LaTeX tables into"
    )
    parser.add_argument(
        "--iterations-table",
        type=str,
        default=DEFAULT_FILES["iterations_table_file"],
        help="File to write the iterations LaTeX table into"
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
        "--no-intel",
        action="store_true",
        help="Do not include Intel compiler results if present in data"
    )
    parser.add_argument(
        "--no-scripts",
        action="store_true",
        help="Do not include any results from scripting languages"
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
#   2. Any iteration that has a negative value for any of the numerical keys
#      is suitably noted and adjusted back into range.
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
            struct[language][algorithm].sort(key=itemgetter("iteration"))

    return struct, languages, algorithms


# Do the analysis over the data. Determine means, medians, etc.
def analyze_data(data, langs, algos):
    new_data = {}

    for lang in langs:
        if lang not in new_data:
            new_data[lang] = {"combined": {}}

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
                # Add to the running combined value:
                new_data[lang]["combined"][key] = \
                    new_data[lang]["combined"].get(key, 0.0) + cell["mean"]

    return new_data


# Create a bar graph for run-times or memory usage by algorithm.
def simple_graph(which, data, filename, *, languages=LANGUAGES, large=False):
    if which not in SIMPLE_GRAPH_PARAMS:
        print(f"  Unknown graph type: {which}")
        return

    key, ylabel, title, legend = SIMPLE_GRAPH_PARAMS[which]

    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    step_off = (len(languages) - 1) / 2
    steps = list(map(lambda x: x * step, range(len(languages))))
    x_len = len(ALGORITHMS)
    x = np.arange(x_len)

    bars = {}
    for lang in languages:
        bars[lang] = np.zeros(x_len, dtype=float)
        for idx, algo in enumerate(ALGORITHMS):
            bars[lang][idx] = data[lang][algo][key]["mean"]

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], bars[lang],
               step, label=LANGUAGE_LABELS[lang])

    ax.set_xticks(
        x + step * step_off, map(lambda a: ALGORITHM_LABELS[a], ALGORITHMS)
    )
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc=legend)

    fig.tight_layout()
    print(f"  Writing {filename}")
    fig.savefig(filename)

    return


# Create a stacked bar graph for energy used by algorithm.
def power_graph(
    data, filename, average=False, *, languages=LANGUAGES, large=False
):
    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    step_off = (len(languages) - 1) / 2
    steps = list(map(lambda x: x * step, range(len(languages))))
    x_len = len(ALGORITHMS)
    x = np.arange(x_len)

    runtimes = {}
    for lang in languages:
        runtimes[lang] = np.array(
            [data[lang][algo]["total_runtime"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )

    pp0 = {}
    for lang in languages:
        pp0[lang] = np.array(
            [data[lang][algo]["pp0"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )

    dram = {}
    for lang in languages:
        dram[lang] = np.array(
            [data[lang][algo]["dram"]["mean"] for algo in ALGORITHMS],
            dtype=float
        )

    if average:
        for lang in languages:
            pp0[lang] /= runtimes[lang]
            dram[lang] /= runtimes[lang]

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], pp0[lang], step,
               label=f"{LANGUAGE_LABELS[lang]}")
        ax.bar(x + steps[idx], dram[lang], step, bottom=pp0[lang])

    ax.set_xticks(
        x + step * step_off, map(lambda a: ALGORITHM_LABELS[a], ALGORITHMS)
    )
    if average:
        ax.set_ylabel("Joules/Second")
        ax.set_title("Energy Use (CPU + DRAM) by Algorithm (per second)")
    else:
        ax.set_ylabel("Joules")
        ax.set_title("Energy Use (CPU + DRAM) by Algorithm")
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
    label=None, divisor=None
):
    global tables_written

    tables_written += 1
    if label:
        print(f"  Creating table {label}")
    else:
        print(f"  Creating table #{tables_written}")

    if type(langs) != list:
        langs = [langs]
    if type(algos) != list:
        algos = [algos]
    if type(fields) != list:
        fields = [fields]
    if divisor is not None:
        if type(divisor) != list:
            divisor = [divisor]

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

    # Create the table of numbers for the data:
    table_data = np.zeros((height, width))
    # Create the table for the divisors (if any):
    divisors = np.zeros((height, width))
    for y_idx, y_str in enumerate(y_axis):
        for x_idx, x_str in enumerate(x_axis):
            if axis == "algorithms":
                table_data[y_idx][x_idx] = \
                    sum([data[y_str][x_str][key]["mean"] for key in fields])
                if divisor:
                    divisors[y_idx][x_idx] = \
                        sum([data[y_str][x_str][key]["mean"]
                            for key in divisor])
            else:
                table_data[y_idx][x_idx] = \
                    sum([data[x_str][y_str][key]["mean"] for key in fields])
                if divisor:
                    divisors[y_idx][x_idx] = \
                        sum([data[x_str][y_str][key]["mean"]
                            for key in divisor])
    # If divisor is set, divide across table_data:
    if divisor:
        table_data /= divisors
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
    print(f"%% Caption: {caption}", file=f)
    print(f"%% Label: table:{label}", file=f)
    print(f"%% Language(s): {langs}", file=f)
    print(f"%% Algorithm(s): {algos}", file=f)
    print(f"%% Field(s): {fields}", file=f)
    if divisor:
        print(f"%% Divisor(s): {divisor}", file=f)
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

    return


# Create all the basic tables, using `data` and the `filename` given.
def create_basic_tables(data, languages, filename):
    with open(filename, "w", encoding="utf-8") as f:
        # Create each table individually.

        # Create a run-time table for each algorithm:
        for algo in ALGORITHMS + APPROX_ALGORITHMS:
            create_computed_table(
                f, data, languages, algo, "runtime",
                caption=f"{ALGORITHM_LABELS[algo]} run-times",
                label=f"runtime:{algo}"
            )

        # Create a pp0/dram energy-usage table for each algorithm:
        for algo in ALGORITHMS + APPROX_ALGORITHMS:
            create_computed_table(
                f, data, languages, algo, ["pp0", "dram"],
                caption=f"{ALGORITHM_LABELS[algo]} PP0/DRAM energy usage",
                label=f"energy:{algo}"
            )

        # Create a package+dram energy-usage-per-second table per algorithm:
        for algo in ALGORITHMS + APPROX_ALGORITHMS:
            caption = f"{ALGORITHM_LABELS[algo]} energy usage over run-time"
            create_computed_table(
                f, data, languages, algo, ["package", "dram"],
                caption=caption, label=f"energy_runtime:{algo}",
                divisor="total_runtime"
            )

        # Create a max-memory table for each algorithm:
        for algo in ALGORITHMS + APPROX_ALGORITHMS:
            caption = \
                f"{ALGORITHM_LABELS[algo]} total memory usage"
            create_computed_table(
                f, data, languages, algo, "max_memory",
                caption=caption, label=f"memory:{algo}"
            )

    return


def create_iterations_table(data, languages, filename):
    algorithms = \
        ALGORITHMS + [APPROX_ALGORITHMS[0]] + [SCRIPT_ONLY_ALGORITHMS[0]]
    algo_labels = [ALGORITHM_LABELS[a] for a in ALGORITHMS]
    algo_labels.append("DFA-Gap")
    algo_labels.append("Regexp-Gap")
    algo_headings = "&".join(algo_labels)
    colspec = "|".join(["c"] * len(algo_labels))

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Algorithm iteration counts", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        # Start the table:
        print(f"\\begin{{tabular}}{{|c|{colspec}|}}", file=f)
        print("\\hline", file=f)
        print(f"Language&{algo_headings} \\\\", file=f)
        print("\\hline", file=f)
        # Table data:
        for lang in languages:
            out = [LANGUAGE_LABELS[lang]]
            for a in algorithms:
                if a in data[lang]:
                    out.append(str(data[lang][a]["runtime"]["samples"]))
                else:
                    out.append("n/a")
            print(f"{'&'.join(out)} \\\\", file=f)
        # Finish out the table:
        print("\\hline", file=f)
        print("\\end{tabular}", file=f)

    return


# Main loop. Read the data, validate it, turn it into useful structure.
def main():
    args = parse_command_line()

    target_languages = LANGUAGES
    if args.no_intel:
        target_languages = list(
            filter(lambda x: not x.endswith("-intel"), target_languages)
        )
    if not args.no_scripts:
        all_languages = target_languages + SCRIPT_LANGUAGES
    else:
        all_languages = target_languages

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
        print("\nDump of data...")
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(analyzed)

    if not args.no_plots:
        print("\nCreating runtimes graph...")
        simple_graph(
            "runtime", analyzed, args.runtimes, languages=target_languages
        )
        print("  Done.")
        if not args.no_scripts:
            print("\nCreating script runtimes graph...")
            simple_graph(
                "runtime", analyzed, args.script_runtimes,
                languages=SCRIPT_LANGUAGES
            )
            print("  Done.")
        print("\nCreating power usage graph...")
        power_graph(analyzed, args.power, languages=target_languages)
        print("  Done.")
        if not args.no_scripts:
            print("\nCreating script power usage graph...")
            power_graph(
                analyzed, args.script_power, languages=SCRIPT_LANGUAGES
            )
            print("  Done.")
        print("\nCreating power-per-second usage graph...")
        power_graph(
            analyzed, args.power_per_sec, True, languages=all_languages,
            large=True
        )
        print("  Done.")

    if not args.no_tables:
        print("\nCreating basic tables...")
        create_basic_tables(analyzed, all_languages, args.basic_tables)
        print("Creating table of iteration counts...")
        create_iterations_table(analyzed, all_languages, args.iterations_table)

    print("\nDone.")

    return


if __name__ == "__main__":
    main()
