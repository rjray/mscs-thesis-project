# Repository for my MSCS Thesis Work

This repository holds all the files (source code, LaTeX, etc.) for my thesis
project, "Evaluating Languages for Bioinformatics: Performance, Expressiveness
and Energy".

This project performs comparisons of five langauges: C, C++, Perl, Python and
Rust. Measurements are taken on relative performance, expressiveness and energy
usage. A variety of string-matching algorithms are implemented and applied to
simulated DNA sequence data.

The directory `src` contains all the program source code for all languages and
for the harness utility used to run the experiments.

The directory `thesis` contains all the LaTeX source for the thesis, as well as
image files used for some of the diagrams.

In addition, the following files are also present in this top-level directory:

* **compression-20221111.txt** - Snapshot of the compression data
* **cyclomatic-20221111.csv**
* **cyclomatic-20221111.json**
* **cyclomatic-20221111.yaml** - Snapshot of the cyclomatic complexity data
* **draft-20221116.pdf** - The draft as submitted to the thesis committee on 2022-11-16
* **experiments-data-20221111.yml**
* **experiments-data-20221120.yml**
* **experiments-data-20221124.yml** - Preserved data from full experiments runs. The 2022-11-11 data was used for all tables and diagrams in the thesis. The others are subsequent full runs of the experiments for comparison purposes.
* **sloc-20221111.csv** - Snapshot of the SLOC data
