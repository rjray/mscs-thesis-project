#!/usr/bin/env python3

# Calculate and graph confidence intervals using one or more datasets

import argparse
import datetime
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
from scipy.stats import t
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
ALGORITHM_TABLE_HEADERS = {
    "kmp": "Knuth-\\\\Morris-\\\\Pratt",
    "boyer_moore": "Boyer-\\\\Moore",
    "shift_or": "Bitap",
    "aho_corasick": "Aho-\\\\Corasick",
    "dfa_gap(1)": "DFA-\\\\Gap",
    "regexp(1)": "Regexp-\\\\Gap",
}

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
        nargs="+",
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
            new_data[lang][algo]["samples"] = len(iters)

            for key in NUMERICAL_KEYS:
                cell = {}
                values = np.array(list(map(lambda x: x[key], iters)))
                size = len(values)
                cell["samples"] = size
                cell["values"] = values
                new_data[lang][algo][key] = cell

    return new_data


def read_and_process(filenames):
    print(f"Processing {len(filenames)} files:")
    data = []
    for filename in filenames:
        print(f"\n  Reading experiments data from {filename}...")
        local_data = []
        with open(filename, "r") as file:
            for record in yaml.safe_load_all(file):
                local_data.append(record)
        print(f"    {len(local_data)} experiment records read.")
        data += local_data

    print(f"\nAll data read, {len(data)} total records gathered.\n")

    print("Validating all data...")
    if not validate(data):
        print("  Validation failed.")
        exit(1)
    print("  Data valid.")

    print("Building data structure...")
    struct, languages, algorithms = build_structure(data)
    print("  Done.")

    print("Analysis of data...")
    analyzed = analyze_data(struct, languages, algorithms)
    print("  Done.")

    return analyzed


# Get the figure and axes objects for a new plot.
def get_fig_and_ax(large=True):
    if large:
        fig, ax = plt.subplots(figsize=(7.5, 5.6), dpi=100.0)
    else:
        fig, ax = plt.subplots()

    return fig, ax


def create_combined(
    data, language, algorithms, fields, *, filename=None, title=None,
    ylabel=None
):
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

    fig, ax = get_fig_and_ax()

    for idx, algo in enumerate(algorithms):
        cell = data[language][algo]
        samples = cell["samples"]
        xs = np.linspace(1, samples, samples)
        points = np.zeros(cell["samples"])
        for field in fields:
            points += cell[field]["values"]
        a, b = np.polyfit(xs, points, deg=1)
        y_est = a * xs + b
        yerr = xs.std() * np.sqrt(1 / len(xs) +
                                  (xs - xs.mean())**2 /
                                  np.sum((xs - xs.mean())**2))
        y = points

        ax.plot(xs, y_est, '-', color=colors[idx], alpha=0.75)
        ax.fill_between(xs, y - yerr, y + yerr, color=colors[idx], alpha=0.2)
        ax.plot(
            xs, points, ".", color=colors[idx], label=ALGORITHM_LABELS[algo]
        )

    ax.set_ylabel(ylabel)
    ax.set_xlabel(f"Number of samples = {samples}")
    ax.set_title(title)
    ax.legend()
    print(f"  Writing {filename}")
    fig.savefig(filename)


def create_graphs(data, language):
    create_combined(
        data, language, ALGORITHMS, ["runtime"],
        filename=f"cb_{language}-exact.png", ylabel="Seconds",
        title=f"{LANGUAGE_LABELS[language]} Confidence Bands, Exact-Matching Algorithms"
    )
    create_combined(
        data, language, APPROX_ALGORITHMS[:5], ["runtime"],
        filename=f"cb_{language}-dfa.png", ylabel="Seconds",
        title=f"{LANGUAGE_LABELS[language]} Confidence Bands, DFA-Gap Algorithms"
    )
    create_combined(
        data, language, APPROX_ALGORITHMS[5:], ["runtime"],
        filename=f"cb_{language}-regexp.png", ylabel="Seconds",
        title=f"{LANGUAGE_LABELS[language]} Confidence Bands, Regexp-Gap Algorithms"
    )


def calculate_ci(values, confidence):
    m = values.mean()
    s = values.std()
    dof = len(values) - 1

    t_crit = np.abs(t.ppf((1 - confidence) / 2, dof))
    z = s * t_crit / np.sqrt(len(values))

    return (m - z, m + z)


def create_table(
    data, algorithm, fields, *, filename=None, caption=None, label=None
):
    # Set up headers and colspec:
    headers = ["Language"] + ["Low", "High"] * 3
    headers = list(map(lambda x: f"\\thead{{{x}}}", headers))
    headers = " & ".join(headers)
    ci_headers = ["90\\%", "95\\%", "99\\%"]
    ci_headers = list(
        map(lambda x: f"\\thead{{{x} \\\\ Confidence}}", ci_headers)
    )
    ci_headers = list(
        map(lambda x: f"\\multicolumn{{2}}{{c|}}{{{x}}}", ci_headers)
    )
    ci_headers = " & ".join(ci_headers)
    colspec = "|c|r|r|r|r|r|r|"

    # Set up the rows:
    rows = []
    for lang in LANGUAGES[:-2]:
        cell = data[lang][algorithm]
        samples = cell["samples"]
        row = [f"\\makecell{{{LANGUAGE_LABELS[lang]} \\\\ (N={samples})}}"]
        values = np.zeros(samples)
        for field in fields:
            values += cell[field]["values"]
        for conf in [0.90, 0.95, 0.99]:
            lo, hi = calculate_ci(values, conf)
            row.append(f"{lo:.4f}")
            row.append(f"{hi:.4f}")

        rows.append(row)

    with open(filename, "w", encoding="utf-8") as f:
        print(f"% Table: {caption}", file=f)
        print(f"% Generated: {datetime.datetime.now()}", file=f)
        print("\\begin{table}[h!]", file=f)
        print("    \\begin{center}", file=f)
        print(f"        \\begin{{tabular}}{{{colspec}}}", file=f)
        print("            \\hline", file=f)
        print(f"            & {ci_headers} \\\\", file=f)
        print("            \\hline", file=f)
        print(f"            {headers} \\\\", file=f)
        print("            \\hline", file=f)
        for row in rows:
            content = " & ".join(row)
            print(f"            {content} \\\\", file=f)
            print("            \\hline", file=f)
        print("        \\end{tabular}", file=f)
        print(f"        \\caption{{{caption}}}", file=f)
        print(f"        \\label{{{label}}}", file=f)
        print("    \\end{center}", file=f)
        print("\\end{table}", file=f)

    return


def create_tables(data):
    # First do the exact-matching algorithms:
    for algo in ALGORITHMS:
        create_table(
            data, algo, ["runtime"], filename=f"ci_runtime_{algo}.tex",
            label=f"table:ci:runtime:{algo}",
            caption=f"Runtime Confidence Intervals for {ALGORITHM_LABELS[algo]}"
        )
        create_table(
            data, algo, ["package", "dram"], filename=f"ci_energy_{algo}.tex",
            label=f"table:ci:energy:{algo}",
            caption=f"Energy usage Confidence Intervals for {ALGORITHM_LABELS[algo]}"
        )

    # Do DFA and Regexp, only for k=3:
    for algo in ["dfa_gap(3)", "regexp(3)"]:
        create_table(
            data, algo, ["runtime"], filename=f"ci_runtime_{algo}.tex",
            label=f"table:ci:runtime:{algo}",
            caption=f"Runtime Confidence Intervals for {ALGORITHM_LABELS[algo]}"
        )
        create_table(
            data, algo, ["package", "dram"], filename=f"ci_energy_{algo}.tex",
            label=f"table:ci:energy:{algo}",
            caption=f"Energy usage Confidence Intervals for {ALGORITHM_LABELS[algo]}"
        )

    return


def main():
    args = parse_command_line()

    data = read_and_process(args.input)

    # for lang in LANGUAGES:
    #     print(f"Generating graphs for {lang}...")
    #     create_graphs(data, lang)

    print("Generating tables...")
    create_tables(data)

    return


if __name__ == "__main__":
    main()
