#!/usr/bin/env python3

# Process the results from running the full test harness.

import argparse
import csv
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import re
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
ALGORITHM_TABLE_HEADERS = {
    "kmp": "Knuth-\\\\Morris-\\\\Pratt",
    "boyer_moore": "Boyer-\\\\Moore",
    "shift_or": "Bitap",
    "aho_corasick": "Aho-\\\\Corasick",
    "dfa_gap(1)": "DFA-\\\\Gap",
    "regexp(1)": "Regexp-\\\\Gap",
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
UNIQUE_LANGUAGES = ["C", "C++", "Perl", "Python", "Rust"]

DEFAULT_FILES = {
    "data": "experiments_data.yml",
    "compression_data": "compression.txt",
    "sloc_data": "sloc.csv",
    "cyclomatic_data": "cyclomatic.%s",
    "runtimes_graph": "runtimes.png",
    "power_graph": "power.png",
    "pps_graph": "power_per_sec.png",
    "script_runtimes_graph": "runtimes-scripts.png",
    "script_power_graph": "power-scripts.png",
    "iterations_table_file": "iterations.tex",
    "runtimes_table_file": "runtimes.tex",
    "energy_table_file": "energy.tex",
    "compression_table_file": "compression.tex",
    "sloc_table_file": "sloc.tex",
    "cyclomatic_table_file": "cyclomatic.tex",
}

SIMPLE_GRAPH_PARAMS = {
    "runtime": [
        "runtime", "Seconds", "Run-Time Comparison by Algorithm", "upper right"
    ],
    "memory": [
        "max_memory", "Megabytes", "Memory Usage by Algorithm", "lower right"
    ],
}


# Grab command-line arguments for the script.
def parse_command_line():
    parser = argparse.ArgumentParser()

    # Set up the arguments
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_FILES["data"],
        help="Input YAML data to process"
    )
    parser.add_argument(
        "--compression-data",
        type=str,
        default=DEFAULT_FILES["compression_data"],
        help="File to read compression data from"
    )
    parser.add_argument(
        "--sloc-data",
        type=str,
        default=DEFAULT_FILES["sloc_data"],
        help="File to read SLOC data from"
    )
    parser.add_argument(
        "--cyclomatic-data",
        type=str,
        default=DEFAULT_FILES["cyclomatic_data"],
        help="File to read cyclomatic data from (use '%s' for extensions)"
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
        "--iterations-table",
        type=str,
        default=DEFAULT_FILES["iterations_table_file"],
        help="File to write the iterations LaTeX table into"
    )
    parser.add_argument(
        "--runtimes-table",
        type=str,
        default=DEFAULT_FILES["runtimes_table_file"],
        help="File to write the runtimes LaTeX table into"
    )
    parser.add_argument(
        "--energy-table",
        type=str,
        default=DEFAULT_FILES["energy_table_file"],
        help="File to write the energy LaTeX table into"
    )
    parser.add_argument(
        "--compression-table",
        type=str,
        default=DEFAULT_FILES["compression_table_file"],
        help="File to write the compression LaTeX table into"
    )
    parser.add_argument(
        "--sloc-table",
        type=str,
        default=DEFAULT_FILES["sloc_table_file"],
        help="File to write the SLOC LaTeX table into"
    )
    parser.add_argument(
        "--cyclomatic-table",
        type=str,
        default=DEFAULT_FILES["cyclomatic_table_file"],
        help="File to write the cyclomatic LaTeX table into"
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
            if algorithm in struct[language]:
                struct[language][algorithm].sort(key=itemgetter("iteration"))

    return struct, languages, algorithms


# Do the analysis over the data. Determine means, medians, etc.
def analyze_data(data, langs, algos):
    new_data = {}

    for lang in langs:
        if lang not in new_data:
            new_data[lang] = {"combined": {}}

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
                # Add to the running combined value:
                new_data[lang]["combined"][key] = \
                    new_data[lang]["combined"].get(key, 0.0) + cell["mean"]

    return new_data


# Read the compression stats from the given file. Return a dict indexed by the
# elements of UNIQUE_LANGUAGES.
def read_compression(filename):
    raw_data = {}
    with open(filename, "r") as f:
        for line in f:
            m = re.search(r"compression/([\w+]+)[.]tar:.*= (\d+[.]\d+)", line)
            if m:
                raw_data[m.group(1)] = float(m.group(2))
            else:
                print(f">>> Bad line read from {filename}: {line}")

    return raw_data


# Read the SLOC data (CSV format) and create a structure with two values for
# each of UNIQUE_LANGUAGES: with and without input/runner modules.
def read_sloc(filename):
    raw_data = {}
    for lang in UNIQUE_LANGUAGES:
        raw_data[lang] = {}

    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            path = row["Path"]
            lines = row["Source"]
            lang, file = path.split("/", maxsplit=1)
            raw_data[lang][file] = int(lines)

    # Make the data we'll return
    data = {}

    # Process C, C++ and Python identically:
    for lang in ["C", "C++", "Python"]:
        data[lang] = [0, 0, 0]
        for path, lines in raw_data[lang].items():
            # Skip the regexp code for now:
            if path.startswith("regexp"):
                continue
            # Index 0 is "all", index 1 is "without boilerplate", index 2 is
            # for the boilerplate.
            data[lang][0] += lines
            if path.startswith("run.") or path.startswith("input."):
                data[lang][2] += lines
            else:
                data[lang][1] += lines
    # Process Perl mostly the same:
    data["Perl"] = [0, 0, 0]
    for path, lines in raw_data["Perl"].items():
        # Skip the regexp code for now:
        if path.startswith("regexp"):
            continue
        # Index 0 is "all", index 1 is "without boilerplate", index 2 is for
        # the boilerplate.
        data["Perl"][0] += lines
        if path.startswith("Run") or path.startswith("Input"):
            data["Perl"][2] += lines
        else:
            data["Perl"][1] += lines
    # Rust is more unique:
    data["Rust"] = [0, 0, 0]
    for path, lines in raw_data["Rust"].items():
        # Index 0 is "all", index 1 is "without boilerplate", index 2 is for
        # the boilerplate.
        data["Rust"][0] += lines
        if path.startswith("common"):
            data["Rust"][2] += lines
        else:
            data["Rust"][1] += lines

    return data


# Read the cyclomatic complexity data. This means reading two files: one CSV,
# one JSON. The JSON data is for Perl only, and the CSV is for the others.
# Merge the data into a single structure.
#
# `filename` should have a "%s" in it for the suffixes.
def read_cyclomatic(filename):
    csv_filename = filename % "csv"
    json_filename = filename % "json"
    yaml_filename = filename % "yaml"

    raw_data = {lang: {} for lang in UNIQUE_LANGUAGES}

    # First the CSV data. This covers C, C++, and Python.
    csv_data = []
    with open(csv_filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_data.append([row[6], int(row[1])])
    # Sort by file name. This includes the language name, too.
    csv_data.sort(key=itemgetter(0))
    tmpmap = {}
    for file, count in csv_data:
        if file not in tmpmap:
            tmpmap[file] = []
        tmpmap[file].append(count)
    for name, values in tmpmap.items():
        total = sum(values)
        lang, file = name.split("/", maxsplit=1)
        raw_data[lang][file] = [total, total / len(values)]

    # Process the Perl data, which is in JSON format.
    json_data = []
    with open(json_filename, "r") as jsonfile:
        data = json.load(jsonfile)
    for record in data["subs"]:
        # Discard the code outside of subs because Lizard did the same with
        # the other languages.
        if not record["name"].startswith("{"):
            name = record["path"].split("/", maxsplit=1)[1]
            json_data.append(
                [name, record["mccabe_complexity"]]
            )
    # Sort by file name.
    json_data.sort(key=itemgetter(0))
    tmpmap = {}
    for file, count in json_data:
        if file not in tmpmap:
            tmpmap[file] = []
        tmpmap[file].append(count)
    for file, values in tmpmap.items():
        total = sum(values)
        raw_data["Perl"][file] = [total, total / len(values)]

    # Now process the Rust data, which is in YAML format.
    with open(yaml_filename, "r") as yamlfile:
        for record in yaml.safe_load_all(yamlfile):
            name = record["name"].split("/", maxsplit=1)[1]
            total = int(record["metrics"]["cyclomatic"]["sum"])
            average = record["metrics"]["cyclomatic"]["average"]
            raw_data["Rust"][name] = [total, average]

    # These are not counted for the research:
    del raw_data["Perl"]["regexp.pl"]
    del raw_data["Python"]["regexp.py"]
    del raw_data["Rust"]["common/src/lib.rs"]

    return raw_data


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
    # Algorithms
    algorithms = ALGORITHMS + [APPROX_ALGORITHMS[0]]
    # Total width of each algorithm's bars
    width = 0.8
    step = width / len(languages)
    step_off = (len(languages) - 1) / 2
    steps = list(map(lambda x: x * step, range(len(languages))))
    x_len = len(algorithms)
    x = np.arange(x_len)

    runtimes = {}
    for lang in languages:
        runtimes[lang] = np.array(
            [data[lang][algo]["total_runtime"]["mean"] for algo in algorithms],
            dtype=float
        )

    package = {}
    for lang in languages:
        package[lang] = np.array(
            [data[lang][algo]["package"]["mean"] for algo in algorithms],
            dtype=float
        )

    dram = {}
    for lang in languages:
        dram[lang] = np.array(
            [data[lang][algo]["dram"]["mean"] for algo in algorithms],
            dtype=float
        )

    if average:
        for lang in languages:
            package[lang] /= runtimes[lang]
            dram[lang] /= runtimes[lang]

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], package[lang], step,
               label=f"{LANGUAGE_LABELS[lang]}")
        ax.bar(x + steps[idx], dram[lang], step, bottom=package[lang])

    ax.set_xticks(
        x + step * step_off, map(lambda a: ALGORITHM_LABELS[a], algorithms)
    )
    if average:
        ax.set_ylabel("Joules/Second")
        ax.set_title("Energy Use (Package + DRAM) by Algorithm (per second)")
    else:
        ax.set_ylabel("Joules")
        ax.set_title("Energy Use (Package + DRAM) by Algorithm")
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
    f, data, langs, algorithm, fields, *, caption=None, label=None,
    divisor=None
):
    if label:
        print(f"    Creating table {label}")
    else:
        print(f"    Creating table for {algorithm}")

    if type(langs) != list:
        langs = [langs]
    if type(fields) != list:
        fields = [fields]
    if divisor is not None:
        if type(divisor) != list:
            divisor = [divisor]

    lang_labels = list(map(lambda l: LANGUAGE_LABELS[l], langs))

    length = len(langs)
    y_axis = langs
    y_labels = lang_labels

    colspec = "l|r"
    headers = "Language & Score"

    # Create the vector of numbers for the data:
    table_data = np.zeros(length)
    # Create the vector for the divisors (if any):
    divisors = np.zeros(length)
    for y_idx, y_str in enumerate(y_axis):
        table_data[y_idx] = \
            sum([data[y_str][algorithm][key]["mean"] for key in fields])
        if divisor:
            divisors[y_idx] = \
                sum([data[y_str][algorithm][key]["mean"] for key in divisor])
    # If divisor is set, divide across table_data:
    if divisor:
        table_data /= divisors
    # Normalize:
    table_data /= table_data.min()

    # Now we need a map of the order to display rows in.
    row_map = list(range(length))
    row_map.sort(key=lambda i: table_data[i])

    # Emit the preamble:
    print(f"    \\begin{{tabular}}{{|{colspec}|}}", file=f)
    print(f"        %% Caption: {caption}", file=f)
    print(f"        %% Label: table:{label}", file=f)
    print(f"        %% Field(s): {fields}", file=f)
    if divisor:
        print(f"        %% Divisor(s): {divisor}", file=f)
    print("        \\hline", file=f)
    print(f"        {headers} \\\\", file=f)
    print("        \\hline", file=f)

    for y_idx in row_map:
        row = [y_labels[y_idx]]
        row.append(f"{table_data[y_idx]:.4f}")
        print("        " + " & ".join(row) + " \\\\", file=f)

    print("        \\hline", file=f)
    print("    \\end{tabular}", file=f)
    # Caption and label:
    print(f"    \\caption{{{caption}}}", file=f)
    print(f"    \\label{{table:{label}}}", file=f)

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


# Create the table breaking down the iterations done for each combination of
# language and algorithm.
def create_iterations_table(data, languages, filename):
    algorithms = \
        ALGORITHMS + [APPROX_ALGORITHMS[0]] + [SCRIPT_ONLY_ALGORITHMS[0]]
    table_labels = [ALGORITHM_TABLE_HEADERS[a] for a in algorithms]
    table_labels = list(map(lambda x: f"\\thead{{{x}}}", table_labels))
    table_headings = " & ".join(table_labels)
    colspec = "|".join(["c"] * len(table_labels))

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Algorithm iteration counts", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        # Start the table:
        print(f"\\begin{{tabular}}{{|c|{colspec}|}}", file=f)
        print("    \\hline", file=f)
        print(f"    \\thead{{Language}} & {table_headings} \\\\", file=f)
        print("    \\hline", file=f)
        # Table data:
        for lang in languages:
            out = [LANGUAGE_LABELS[lang]]
            for a in algorithms:
                if a in data[lang]:
                    out.append(str(data[lang][a]["runtime"]["samples"]))
                else:
                    out.append("n/a")
            print(f"    {' & '.join(out)} \\\\", file=f)
        # Finish out the table:
        print("    \\hline", file=f)
        print("\\end{tabular}", file=f)

    return


# Create the table-of-tables for the run-time scores of the different
# languages on the various algorithms.
def create_runtime_tables(data, languages, filename):
    algorithms = ALGORITHMS + APPROX_ALGORITHMS

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Comparative runtimes sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        for idx, algo in enumerate(algorithms):
            # Start the sub-table:
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            create_computed_table(
                f, data, languages, algo, "runtime",
                caption=ALGORITHM_LABELS[algo], label=f"runtime:{algo}"
            )
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")
            if idx % 3 == 2 or idx == len(algorithms) + 1:
                print("", file=f)
            else:
                print("%", file=f)

    return


# Create the table-of-tables for the values of energy usage over time for the
# languages on the various algorithms.
def create_energy_tables(data, languages, filename):
    algorithms = ALGORITHMS + APPROX_ALGORITHMS

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Comparative energy usage sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        for idx, algo in enumerate(algorithms):
            # Start the sub-table:
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            create_computed_table(
                f, data, languages, algo, ["package", "dram"],
                caption=ALGORITHM_LABELS[algo], label=f"energy:{algo}",
                divisor="total_runtime"
            )
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")
            if idx % 3 == 2 or idx == len(algorithms) + 1:
                print("", file=f)
            else:
                print("%", file=f)

    return


# Create the single table of data for the compression stats.
def create_compression_table(data, filename):
    vector = np.array([data[x] for x in UNIQUE_LANGUAGES])
    scaled = vector / vector.min()
    row_map = list(range(len(UNIQUE_LANGUAGES)))
    row_map.sort(key=lambda i: scaled[i])

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Compression ratios table", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        print("\\centering", file=f)
        print("\\begin{tabular}{|l|c|c|}", file=f)
        print("    \\hline", file=f)
        print("    Language & Ratio & Score \\\\", file=f)
        print("    \\hline", file=f)
        for x in row_map:
            row = [UNIQUE_LANGUAGES[x]]
            ratio = vector[x] * 100
            row.append(f"{ratio:.2f}\\%")
            row.append(f"{scaled[x]:.4f}")
            print("    " + " & ".join(row) + " \\\\", file=f)
        print("    \\hline", file=f)
        print("\\end{tabular}", file=f)

    return


# Create the row of three tables for the SLOC data.
def create_sloc_tables(data, filename):
    all = np.array([data[x][0] for x in UNIQUE_LANGUAGES])
    all_scaled = all / all.min()
    no_bp = np.array([data[x][1] for x in UNIQUE_LANGUAGES])
    no_bp_scaled = no_bp / no_bp.min()
    all_bp = np.array([data[x][2] for x in UNIQUE_LANGUAGES])
    all_bp_scaled = all_bp / all_bp.min()

    all_map = list(range(len(UNIQUE_LANGUAGES)))
    all_map.sort(key=lambda i: all_scaled[i])
    no_bp_map = list(range(len(UNIQUE_LANGUAGES)))
    no_bp_map.sort(key=lambda i: no_bp_scaled[i])
    all_bp_map = list(range(len(UNIQUE_LANGUAGES)))
    all_bp_map.sort(key=lambda i: all_bp_scaled[i])

    with open(filename, "w", encoding="utf-8") as f:
        # Print preamble comments:
        print("% Table: Comparative SLOC totals sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        # First sub-table (without boilerplate):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & Code & Score \\\\", file=f)
        print("        \\hline", file=f)
        for x in no_bp_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(no_bp[x]))
            row.append(f"{no_bp_scaled[x]:.4f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Algorithm lines}", file=f)
        print("    \\label{table:sloc:algorithm}", file=f)
        print("\\end{subtable}%", file=f)
        # Second sub-table (boilerplate only):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & Support & Score \\\\", file=f)
        print("        \\hline", file=f)
        for x in all_bp_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(all_bp[x]))
            row.append(f"{all_bp_scaled[x]:.4f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Framework lines}", file=f)
        print("    \\label{table:sloc:framework}", file=f)
        print("\\end{subtable}%", file=f)
        # Third sub-table (all lines):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & All & Score \\\\", file=f)
        print("        \\hline", file=f)
        for x in all_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(all[x]))
            row.append(f"{all_scaled[x]:.4f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Total of lines}", file=f)
        print("    \\label{table:sloc:all}", file=f)
        print("\\end{subtable}", file=f)

    return


# Create the row of three tables for the cyclomatic complexity data.
def create_cyclomatic_tables(data, filename):
    length = len(UNIQUE_LANGUAGES)
    algos_totals = [0] * length
    algos_avgs = [0] * length
    frame_totals = [0] * length
    frame_avgs = [0] * length
    all_totals = [0] * length
    all_avgs = [0] * length

    for idx, lang in enumerate(UNIQUE_LANGUAGES):
        lang_data = data[lang]
        for file, values in lang_data.items():
            all_totals[idx] += values[0]
            all_avgs[idx] += values[1]
            # Do the values go in algos or frame?
            if file.startswith("input") or file.startswith("run"):
                # C/C++/Python
                frame_totals[idx] += values[0]
                frame_avgs[idx] += values[1]
            elif file.startswith("Input") or file.startswith("Run"):
                # Perl
                frame_totals[idx] += values[0]
                frame_avgs[idx] += values[1]
            elif file.startswith("common"):
                # Rust
                frame_totals[idx] += values[0]
                frame_avgs[idx] += values[1]
            else:
                # Goes in under algorithms
                algos_totals[idx] += values[0]
                algos_avgs[idx] += values[1]

    # At this point, the three pairs should be completely filled in. Create the
    # mappings.
    all_map = list(range(length))
    all_map.sort(key=lambda i: all_totals[i])
    algos_map = list(range(length))
    algos_map.sort(key=lambda i: algos_totals[i])
    frame_map = list(range(length))
    frame_map.sort(key=lambda i: frame_totals[i])

    # Create tables.
    with open(filename, "w", encoding="utf-8") as f:
        # Preamble comments:
        print("% Table: Comparative cyclomatic totals sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        # First sub-table (algorithms without boilerplate):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & Total & Avg \\\\", file=f)
        print("        \\hline", file=f)
        for x in algos_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(algos_totals[x]))
            row.append(f"{algos_avgs[x]:.2f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Algorithms complexity}", file=f)
        print("    \\label{table:cyclomatic:algorithm}", file=f)
        print("\\end{subtable}%", file=f)
        # Second sub-table (boilerplate only):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & Total & Avg \\\\", file=f)
        print("        \\hline", file=f)
        for x in frame_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(frame_totals[x]))
            row.append(f"{frame_avgs[x]:.2f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Framework complexity}", file=f)
        print("    \\label{table:cyclomatic:framework}", file=f)
        print("\\end{subtable}%", file=f)
        # Third sub-table (all values):
        print("\\begin{subtable}{0.33\\textwidth}", file=f)
        print("    \\centering", file=f)
        print("    \\begin{tabular}{|c|r|r|}", file=f)
        print("        \\hline", file=f)
        print("        Language & Total & Avg \\\\", file=f)
        print("        \\hline", file=f)
        for x in all_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(all_totals[x]))
            row.append(f"{all_avgs[x]:.2f}")
            print("        " + " & ".join(row) + " \\\\", file=f)
        print("        \\hline", file=f)
        print("    \\end{tabular}", file=f)
        print("    \\caption{Total complexity}", file=f)
        print("    \\label{table:cyclomatic:total}", file=f)
        print("\\end{subtable}", file=f)

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

    print("##################################################################")
    print("# READING DATA")
    print("##################################################################")

    print(f"\nReading experiments data from {args.input}...")
    data = []
    with open(args.input, "r") as file:
        for record in yaml.safe_load_all(file):
            data.append(record)
    print(f"  {len(data)} experiment records read.")

    print("Validating experiments data...")
    if not validate(data):
        print("  Validation failed.")
        exit(1)
    print("  Data valid.")

    print("Building experiments data structure...")
    struct, languages, algorithms = build_structure(data)
    print("  Done.")
    print(f"\nLanguages detected: {languages}")
    print(f"\nAlgorithms detected: {algorithms}")

    print("\nAnalysis of experiments data...")
    analyzed = analyze_data(struct, languages, algorithms)
    print("  Done.")

    print("\nReading compression data...")
    compression_data = read_compression(args.compression_data)
    print("  Done.")

    print("\nReading SLOC data...")
    sloc_data = read_sloc(args.sloc_data)
    print("  Done.")

    print("\nReading cyclomatic data...")
    cyclomatic_data = read_cyclomatic(args.cyclomatic_data)
    print("  Done.")

    if args.dump:
        print("\nDump of data...")
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(analyzed)

    print()
    print("##################################################################")
    print("# CREATING PLOTS AND TABLES")
    print("##################################################################")

    if not args.no_plots:
        # print("\nCreating runtimes graph...")
        # simple_graph(
        #     "runtime", analyzed, args.runtimes, languages=target_languages
        # )
        # print("  Done.")
        # if not args.no_scripts:
        #     print("\nCreating script runtimes graph...")
        #     simple_graph(
        #         "runtime", analyzed, args.script_runtimes,
        #         languages=SCRIPT_LANGUAGES
        #     )
        #     print("  Done.")
        # print("\nCreating power usage graph...")
        # power_graph(analyzed, args.power, languages=target_languages)
        # print("  Done.")
        # if not args.no_scripts:
        #     print("\nCreating script power usage graph...")
        #     power_graph(
        #         analyzed, args.script_power, languages=SCRIPT_LANGUAGES
        #     )
        #     print("  Done.")
        print("\nCreating power-per-second usage graph...")
        power_graph(
            analyzed, args.power_per_sec, True, languages=all_languages,
            large=True
        )
        print("  Done.")

    if not args.no_tables:
        print("\nCreating tables from experiments data...")
        print("  Creating table of iteration counts...")
        create_iterations_table(analyzed, all_languages, args.iterations_table)
        print("  Creating runtime scores table-of-tables...")
        create_runtime_tables(analyzed, all_languages, args.runtimes_table)
        print("  Creating energy scores table-of-tables...")
        create_energy_tables(analyzed, all_languages, args.energy_table)
        print("\nCreating tables from static analysis data...")
        print("  Creating compressibility measurements table...")
        create_compression_table(compression_data, args.compression_table)
        print("  Creating SLOC measurements tables...")
        create_sloc_tables(sloc_data, args.sloc_table)
        print("  Creating cyclomatic measurements tables...")
        create_cyclomatic_tables(cyclomatic_data, args.cyclomatic_table)

    print("\nDone.")

    return


if __name__ == "__main__":
    main()
