# Utility Code

The Python programs in this directory are utilities that were used for various
steps in the research process.

The following packages are required to run these tools:

* Matplotlib - <https://matplotlib.org/>
* Numpy - <https://numpy.org/>
* PyYAML - <https://pyyaml.org/>

## diff_datasets.py

This utility was written to do some simple comparisons between complete runs
of the experiments. It (currently) requires exactly 3 files arguments, each of
which is expected to be a YAML file produced by the experiment run.

Presently, it only measures the percentage change between datasets in each of
run-time (algorithmic, not full) and energy usage (the combination of package
and DRAM energy usage).

## process_results.py

This is a sizable script (2000+ lines) that processes all the data created by
running the full suite of experiments. It also processes the static-analysis
data (the compression, cyclomatic complexity, and SLOC data). It generates
almost all of the tables used in the thesis, and all of the graphs/charts.

All of the file names that are generated are hard-coded; these can be found in
the declaration of `FILES` in the preamble (the variable declarations prior
to the first function definition).

## random_data.py

This utility generates the random data designed to resemble DNA sequences and
findable patterns. Almost all parameters are tunable; run the command with the
`--help` option for a list of parameters that can be passed.

The goal for the data generation was to generate pseudo-random data that could
be replicated for research purposes. It is written to generate a given number
of "sequences" and an accompanying number of patterns taken directly from the
sequences. Each pattern must be findable in at least 0.1% of all sequences in
order to be added to the list.

Running this tool will generate files of:

* Sequences
* Patterns
* Answers

The answers-file provides a count for each pattern/sequence combination that
indicates how many times it should be found. This was used in the per-language
frameworks to verify that the algorithms were actually returning correct
answers.

Later, when an approximate-matching algorithm was added to the set of
experiments, this script was extended to generate answers-files for the
approximate matching. It defaults to values of `k` ranging from 1 to 5, but is
also tunable.
