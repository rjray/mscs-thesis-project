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
APPROX_ALGORITHMS += [f"regexp({k + 1})" for k in range(5)]
ALGORITHM_LABELS = {
    "kmp": "Knuth-Morris-Pratt",
    "boyer_moore": "Boyer-Moore",
    "shift_or": "Bitap",
    "aho_corasick": "Aho-Corasick",
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
UNIQUE_LANGUAGES = ["C", "C++", "Perl", "Python", "Rust"]

FILES = {
    "data": "experiments_data.yml",
    "compression_data": "compression.txt",
    "sloc_data": "sloc.csv",
    "cyclomatic_data": "cyclomatic.%s",
    "total_power_chart": "total_power_usage.png",
    "pps_chart": "power_per_sec.png",
    "dfa_regexp_chart": "dfa_regexp_comp.png",
    "iterations_table": "iterations.tex",
    "runtimes_table": "runtimes.tex",
    "runtimes_appendix_tables": [
        "runtimes_app_dfa.tex", "runtimes_app_regexp.tex"
    ],
    "energy_table": "energy.tex",
    "energy_appendix_tables": [
        "energy_app_dfa.tex", "energy_app_regexp.tex"
    ],
    "compression_table": "compression.tex",
    "sloc_table": "sloc.tex",
    "cyclomatic_table": "cyclomatic.tex",
    "cyclomatic_score_table": "cyclomatic-score.tex",
    "expressiveness_table": "expressiveness.tex",
    "expr2_table": "expressiveness2.tex",
    "expressiveness_graph": "expressiveness_arrows.png",
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
        default=FILES["data"],
        help="Input YAML data to process"
    )
    parser.add_argument(
        "--compression-data",
        type=str,
        default=FILES["compression_data"],
        help="File to read compression data from"
    )
    parser.add_argument(
        "--sloc-data",
        type=str,
        default=FILES["sloc_data"],
        help="File to read SLOC data from"
    )
    parser.add_argument(
        "--cyclomatic-data",
        type=str,
        default=FILES["cyclomatic_data"],
        help="File to read cyclomatic data from (use '%s' for extensions)"
    )
    parser.add_argument(
        "-d",
        "--dump",
        action="store_true",
        help="Dump processed data"
    )

    return parser.parse_args()


# Return a list with the indicies of from_list sorted by the values of
# from_list. The input list is unchanged.
def make_map(from_list):
    new_map = list(range(len(from_list)))
    new_map.sort(key=lambda i: from_list[i])

    return new_map


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


# Read the compression stats from the given file. Return a dict indexed by the
# elements of UNIQUE_LANGUAGES.
def read_compression(filename):
    raw_data = {}
    with open(filename, "r") as f:
        for line in f:
            m = re.search(r"compression/([\w+]+)[.]txt:.*= (\d+[.]\d+)", line)
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
            # Skip the jpcre2.hpp file for C++:
            if path.startswith("jpcre2"):
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
    del raw_data["C++"]["jpcre2.hpp"]
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


def total_power_usage_chart(
    data, filename, *, languages=LANGUAGES, large=False
):
    # Algorithms
    algorithms = ALGORITHMS + APPROX_ALGORITHMS

    # Filter out Perl/Python
    languages = list(filter(lambda x: not x.startswith("p"), languages))

    # Language labels
    labels = [LANGUAGE_LABELS[x] for x in languages]

    # Get the totaled energy usage
    totals = np.zeros(len(languages))
    for idx, lang in enumerate(languages):
        for algo in algorithms:
            totals[idx] += data[lang][algo]["package"]["mean"]
            totals[idx] += data[lang][algo]["dram"]["mean"]
    # Apply a base-10 logarithm to it, because of Perl/Python:
    # totals = np.log10(totals)

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    ax.bar(labels, totals)
    ax.set_ylabel("Joules")
    ax.set_ylim(15000)
    ax.set_title("Total Energy (Package + DRAM) by Language (Compiled Only)")
    ax.axes.tick_params(axis="x", labelrotation=17, labelsize="large")
    ax.axes.axhline(totals.min(), color="r")

    print(f"    Writing {filename}")
    fig.savefig(filename)

    return


# Create bar charts for energy used by each algorithm (Joules/second).
def power_per_second_chart(
    data, filename, *, languages=LANGUAGES, large=False
):
    # Algorithms
    algorithms = ALGORITHMS + [APPROX_ALGORITHMS[0], APPROX_ALGORITHMS[5]]
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

    combined = {}
    for lang in languages:
        combined[lang] = (package[lang] + dram[lang]) / runtimes[lang]

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    for idx, lang in enumerate(languages):
        ax.bar(x + steps[idx], combined[lang], step,
               label=f"{LANGUAGE_LABELS[lang]}")

    ax.set_xticks(
        x + step * step_off, map(lambda a: ALGORITHM_LABELS[a], algorithms)
    )
    ax.axes.tick_params(axis="x", labelrotation=17, labelsize="large")
    ax.set_ylabel("Joules/second")
    ax.set_title("Energy Use (Package + DRAM) by Algorithm (per second)")
    ax.legend(loc="lower right")

    fig.tight_layout()
    print(f"    Writing {filename}")
    fig.savefig(filename)

    return


# Create bar charts for comparing DFA to Regexp for Perl/Python.
def dfa_regexp_charts(data, filename, *, large=False):
    groups = ["perl.dfa_gap", "perl.regexp", "python.dfa_gap", "python.regexp"]
    group_labels = [
        "Perl (DFA)", "Perl (Regexp)", "Python (DFA)", "Python (Regexp)"
    ]
    # Total width of each group's bars
    width = 0.8
    step = width / len(groups)
    step_off = (len(groups) - 1) / 2
    steps = list(map(lambda x: x * step, range(len(groups))))
    x_len = 5
    x = np.arange(x_len)

    combined = {key: np.zeros(x_len) for key in groups}
    # Create the bar data
    for k in range(x_len):
        for lang in ["perl", "python"]:
            for algo in ["dfa_gap", "regexp"]:
                key = f"{lang}.{algo}"
                value = data[lang][f"{algo}({k + 1})"]["runtime"]["mean"]
                combined[key][k] = value

    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    for idx, group in enumerate(groups):
        ax.bar(x + steps[idx], combined[group], step, label=group_labels[idx])

    ax.set_xticks(
        x + step * step_off, map(lambda k: f"k = {k + 1}", range(x_len))
    )
    ax.set_ylabel("Seconds")
    ax.set_title("Comparison of DFA vs. Regexp in Perl/Python")
    ax.legend(loc="upper left")

    fig.tight_layout()
    print(f"    Writing {filename}")
    fig.savefig(filename)

    return


# Create a 3-D graph of arrows coming out from the origin.
def arrow_graph(data, labels, filename):
    ax = plt.figure().add_subplot(projection='3d')

    ax.set(
        xlim=(0, 1),
        ylim=(0, 1),
        zlim=(0, 1),
        xlabel="SLOC",
        ylabel="Complexity",
        zlabel="Compression"
    )

    z = np.zeros(5)
    u, v, w = data.transpose()
    ax.quiver(z, z, z, u, v, w, label=labels)

    print(f"    Writing {filename}")
    plt.savefig(filename)

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
    row_map = make_map(table_data)

    # Caption and label:
    print(f"    \\caption{{{caption}}}", file=f)
    print(f"    \\label{{table:{label}}}", file=f)
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

    return


# Create the table breaking down the iterations done for each combination of
# language and algorithm.
def create_iterations_table(data, filename):
    algorithms = \
        ALGORITHMS + [APPROX_ALGORITHMS[0], APPROX_ALGORITHMS[5]]
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
        for lang in LANGUAGES:
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
def create_runtime_tables(data, filename):
    # Rather than show all 5 instances of DFA and Regexp, show just for k = 3.
    algorithms = ALGORITHMS + [APPROX_ALGORITHMS[2], APPROX_ALGORITHMS[7]]

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Comparative runtimes sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        for idx, algo in enumerate(algorithms):
            # Start the sub-table:
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            create_computed_table(
                f, data, LANGUAGES, algo, "runtime",
                caption=ALGORITHM_LABELS[algo], label=f"runtime:{algo}"
            )
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")
            if idx % 3 == 2 or idx == len(algorithms) - 1:
                print("", file=f)
            else:
                print("%", file=f)

    return


def create_runtime_appendix_tables(data, filenames):
    algo_names = ["DFA-Gap", "Regexp"]
    algo_labels = ["dfa_gap", "regexp"]

    for which, filename in enumerate(filenames):
        algorithms = APPROX_ALGORITHMS[(which * 5):(which * 5 + 5)]
        name = algo_names[which]
        a_label = algo_labels[which]

        with open(filename, "w", encoding="utf-8") as f:
            # Print the preamble comments:
            print(f"% Table: Comparative {name} runtimes sub-tables", file=f)
            print(f"% Generated: {datetime.datetime.now()}", file=f)
            for idx, algo in enumerate(algorithms):
                # Start the sub-table:
                print("\\begin{subtable}{0.33\\textwidth}", file=f)
                print("    \\centering", file=f)
                create_computed_table(
                    f, data, LANGUAGES, algo, "runtime",
                    caption=f"$k={idx + 1}$", label=f"runtime:{algo}"
                )
                # End the sub-table:
                print("\\end{subtable}", file=f, end="")
                if idx % 3 == 2:
                    print("", file=f)
                else:
                    print("%", file=f)

            # Now the combined table:
            print(f"    Creating combined runtimes table for {name}")
            lang_labels = list(map(lambda l: LANGUAGE_LABELS[l], LANGUAGES))
            combined = np.zeros(len(LANGUAGES))
            for idx, lang in enumerate(LANGUAGES):
                for algo in algorithms:
                    combined[idx] += data[lang][algo]["runtime"]["mean"]
            combined /= combined.min()
            combined_map = make_map(combined)
            caption = "Combined $k$"
            label = f"runtime:{a_label}:combined"

            # Start the sub-table
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            # Caption and label:
            print(f"    \\caption{{{caption}}}", file=f)
            print(f"    \\label{{table:{label}}}", file=f)
            # Sub-table
            print("    \\begin{tabular}{|l|r|}", file=f)
            print("        \\hline", file=f)
            print("        Language & Score \\\\", file=f)
            print("        \\hline", file=f)

            for idx in combined_map:
                row = [lang_labels[idx]]
                row.append(f"{combined[idx]:.4f}")
                print("        " + " & ".join(row) + " \\\\", file=f)

            print("        \\hline", file=f)
            print("    \\end{tabular}", file=f)
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")

    return


# Create the table-of-tables for the values of energy usage over time for the
# languages on the various algorithms.
def create_energy_tables(data, filename):
    # Rather than show all 5 instances of DFA and Regexp, show just for k = 3.
    algorithms = ALGORITHMS + [APPROX_ALGORITHMS[2], APPROX_ALGORITHMS[7]]

    with open(filename, "w", encoding="utf-8") as f:
        # Print the preamble comments:
        print("% Table: Comparative energy usage sub-tables", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        for idx, algo in enumerate(algorithms):
            # Start the sub-table:
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            create_computed_table(
                f, data, LANGUAGES, algo, ["package", "dram"],
                caption=ALGORITHM_LABELS[algo], label=f"energy:{algo}",
                divisor="total_runtime"
            )
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")
            if idx % 3 == 2 or idx == len(algorithms) - 1:
                print("", file=f)
            else:
                print("%", file=f)

    return


def create_energy_appendix_tables(data, filenames):
    algo_names = ["DFA-Gap", "Regexp-Gap"]
    algo_labels = ["dfa_gap", "regexp"]

    for which, filename in enumerate(filenames):
        algorithms = APPROX_ALGORITHMS[(which * 5):(which * 5 + 5)]
        name = algo_names[which]
        a_label = algo_labels[which]

        with open(filename, "w", encoding="utf-8") as f:
            # Print the preamble comments:
            print(f"% Table: Comparative {name} energy sub-tables", file=f)
            print(f"% Generated: {datetime.datetime.now()}", file=f)
            for idx, algo in enumerate(algorithms):
                # Start the sub-table:
                print("\\begin{subtable}{0.33\\textwidth}", file=f)
                print("    \\centering", file=f)
                create_computed_table(
                    f, data, LANGUAGES, algo, ["package", "dram"],
                    caption=f"$k={idx + 1}$", label=f"energy:{algo}",
                    divisor="total_runtime"
                )
                # End the sub-table:
                print("\\end{subtable}", file=f, end="")
                if idx % 3 == 2:
                    print("", file=f)
                else:
                    print("%", file=f)

            # Now the combined table:
            print(f"    Creating combined runtimes table for {name}")
            lang_labels = list(map(lambda l: LANGUAGE_LABELS[l], LANGUAGES))
            combined = np.zeros(len(LANGUAGES))
            for idx, lang in enumerate(LANGUAGES):
                for algo in algorithms:
                    combined[idx] += data[lang][algo]["package"]["mean"]
                    combined[idx] += data[lang][algo]["dram"]["mean"]
                    combined[idx] /= data[lang][algo]["total_runtime"]["mean"]
            combined /= combined.min()
            combined_map = make_map(combined)
            caption = "Combined $k$"
            label = f"energy:{a_label}:combined"

            # Start the sub-table
            print("\\begin{subtable}{0.33\\textwidth}", file=f)
            print("    \\centering", file=f)
            # Caption and label:
            print(f"    \\caption{{{caption}}}", file=f)
            print(f"    \\label{{table:{label}}}", file=f)
            # Sub-table
            print("    \\begin{tabular}{|l|r|}", file=f)
            print("        \\hline", file=f)
            print("        Language & Score \\\\", file=f)
            print("        \\hline", file=f)

            for idx in combined_map:
                row = [lang_labels[idx]]
                row.append(f"{combined[idx]:.4f}")
                print("        " + " & ".join(row) + " \\\\", file=f)

            print("        \\hline", file=f)
            print("    \\end{tabular}", file=f)
            # End the sub-table:
            print("\\end{subtable}", file=f, end="")

    return


# Create the single table of data for the compression stats.
def create_compression_table(data, filename):
    vector = np.array([data[x] for x in UNIQUE_LANGUAGES])
    vector = np.ones(len(UNIQUE_LANGUAGES)) - vector
    scaled = vector / vector.min()
    row_map = make_map(scaled)

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

    return scaled


# Create the row of three tables for the SLOC data.
def create_sloc_tables(data, filename):
    all = np.array([data[x][0] for x in UNIQUE_LANGUAGES])
    all_scaled = all / all.min()
    no_bp = np.array([data[x][1] for x in UNIQUE_LANGUAGES])
    no_bp_scaled = no_bp / no_bp.min()
    all_bp = np.array([data[x][2] for x in UNIQUE_LANGUAGES])
    all_bp_scaled = all_bp / all_bp.min()

    all_map = make_map(all_scaled)
    no_bp_map = make_map(no_bp_scaled)
    all_bp_map = make_map(all_bp_scaled)

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

    return all_scaled


# Create the row of three tables for the cyclomatic complexity data and the
# second table-file for the scores from the "all" table.
def create_cyclomatic_tables(data, filename, score_file):
    length = len(UNIQUE_LANGUAGES)
    algos_totals = np.zeros(length, dtype=int)
    algos_avgs = np.zeros(length)
    frame_totals = np.zeros(length, dtype=int)
    frame_avgs = np.zeros(length)
    all_totals = np.zeros(length, dtype=int)
    all_avgs = np.zeros(length)

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
    # mappings and create a third column for "score".
    all_map = make_map(all_totals)
    algos_map = make_map(algos_totals)
    frame_map = make_map(frame_totals)

    # Create tables.
    print(f"    Creating {filename}")
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

    all_score = all_totals / all_totals.min()
    print(f"    Creating {score_file}")
    with open(score_file, "w", encoding="utf-8") as f:
        # Preamble comments:
        print("% Table: Cyclomatic scores for all files", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        print("\\centering", file=f)
        print("\\begin{tabular}{|l|r|r|}", file=f)
        print("    \\hline", file=f)
        print("    Language & Total & Score \\\\", file=f)
        print("    \\hline", file=f)
        for x in all_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(str(all_totals[x]))
            row.append(f"{all_score[x]:.4f}")
            print("    " + " & ".join(row) + " \\\\", file=f)
        print("    \\hline", file=f)
        print("\\end{tabular}", file=f)

    return all_score


def create_expressiveness_tables(
    sloc, cyclomatic, compression, expressiveness, expr2, filename, filename2
):
    expr_map = make_map(expressiveness)
    headings = ["SLOC", "Complexity", "Compression", "Score"]
    headings = list(map(lambda x: f"\\thead{{{x}}}", headings))
    headings = " & ".join(headings)

    print(f"    Writing {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        # Preamble comments:
        print("% Table: Calculated expressiveness score", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        print("\\centering", file=f)
        print("\\begin{tabular}{|l|r|r|r|r|}", file=f)
        print("    \\hline", file=f)
        print(f"    \\thead{{Language}} & {headings} \\\\", file=f)
        print("    \\hline", file=f)
        for x in expr_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(f"{sloc[x]:.4f}")
            row.append(f"{cyclomatic[x]:.4f}")
            row.append(f"{compression[x]:.4f}")
            row.append(f"{expressiveness[x]:.4f}")
            print("    " + " & ".join(row) + " \\\\", file=f)
        print("    \\hline", file=f)
        print("\\end{tabular}", file=f)

    expr_map = make_map(expr2)
    headings = ["SLOC", "Compression", "Score"]
    headings = list(map(lambda x: f"\\thead{{{x}}}", headings))
    headings = " & ".join(headings)

    print(f"    Writing {filename2}")
    with open(filename2, "w", encoding="utf-8") as f:
        # Preamble comments:
        print("% Table: Calculated expressiveness score (2-axis)", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        print("\\centering", file=f)
        print("\\begin{tabular}{|l|r|r|r|}", file=f)
        print("    \\hline", file=f)
        print(f"    \\thead{{Language}} & {headings} \\\\", file=f)
        print("    \\hline", file=f)
        for x in expr_map:
            row = [UNIQUE_LANGUAGES[x]]
            row.append(f"{sloc[x]:.4f}")
            row.append(f"{compression[x]:.4f}")
            row.append(f"{expr2[x]:.4f}")
            print("    " + " & ".join(row) + " \\\\", file=f)
        print("    \\hline", file=f)
        print("\\end{tabular}", file=f)

    return


def combine_axes(*axes):
    # Make each of them into unit vectors:
    axes = list(map(lambda x: x / np.linalg.norm(x), axes))

    combined_axes = map(np.array, zip(*axes))
    return np.array(list(combined_axes))


def calculate_lengths(axes):
    return np.array(list(map(np.linalg.norm, axes)))


# Main loop. Read the data, validate it, turn it into useful structure.
def main():
    args = parse_command_line()

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
        return

    print()
    print("##################################################################")
    print("# CREATING PLOTS AND TABLES")
    print("##################################################################")

    print("\nCreating tables from experiments data...")
    print("  Creating table of iteration counts...")
    create_iterations_table(analyzed, FILES["iterations_table"])
    print("  Creating runtime scores table-of-tables...")
    create_runtime_tables(analyzed, FILES["runtimes_table"])
    print("  Creating runtime scores tables for appendix...")
    create_runtime_appendix_tables(analyzed, FILES["runtimes_appendix_tables"])
    print("  Creating energy scores table-of-tables...")
    create_energy_tables(analyzed, FILES["energy_table"])
    print("  Creating energy scores tables for appendix...")
    create_energy_appendix_tables(analyzed, FILES["energy_appendix_tables"])
    print("\nCreating tables from static analysis data...")
    print("  Creating compressibility measurements table...")
    conciseness_scores = create_compression_table(
        compression_data, FILES["compression_table"]
    )
    print("  Creating SLOC measurements tables...")
    sloc_scores = create_sloc_tables(sloc_data, FILES["sloc_table"])
    print("  Creating cyclomatic measurements tables...")
    cyclomatic_scores = create_cyclomatic_tables(
        cyclomatic_data, FILES["cyclomatic_table"],
        FILES["cyclomatic_score_table"]
    )

    print("\nCreating plots/graphs from core analyzed data...")
    print("  Creating total power usage chart...")
    total_power_usage_chart(analyzed, FILES["total_power_chart"])
    print("  Creating power-per-second usage chart...")
    power_per_second_chart(analyzed, FILES["pps_chart"])
    print("  Done.")
    print("  Creating DFA vs. Regexp Perl/Python runtimes chart...")
    dfa_regexp_charts(analyzed, FILES["dfa_regexp_chart"], large=True)
    print("  Done.")

    print("\nCreating elements from combined/post-processed data...")
    print("  Calculating compound expressiveness scores...")
    expressiveness_axes = combine_axes(
        sloc_scores, cyclomatic_scores, conciseness_scores
    )
    expressiveness_lengths = calculate_lengths(expressiveness_axes)
    expressiveness_scores = \
        expressiveness_lengths / expressiveness_lengths.min()
    expr2_axes = combine_axes(sloc_scores, conciseness_scores)
    expr2_lengths = calculate_lengths(expr2_axes)
    expr2_scores = expr2_lengths / expr2_lengths.min()
    print("  Creating expressiveness tables...")
    create_expressiveness_tables(
        sloc_scores, cyclomatic_scores, conciseness_scores,
        expressiveness_scores, expr2_scores, FILES["expressiveness_table"],
        FILES["expr2_table"]
    )
    print("  Done.")
    # print("  Creating expressiveness arrow graph...")
    # arrow_graph(
    #     expressiveness_axes, UNIQUE_LANGUAGES, FILES["expressiveness_graph"]
    # )
    # print("  Done.")

    # As in, done with everything...
    print("\nDone.")

    return


if __name__ == "__main__":
    main()
