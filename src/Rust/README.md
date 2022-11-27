# Rust Source Code

The source code for the Rust implementation of the experiments is in this
directory. The Rust code follows a different structure than the other languages
as Rust's `cargo` utility manages things as "workspaces". Thus, each of the
algorithms (as well as the framework) is in a separate directory.

In addition to the controlling `Makefile`, the following files are in the base
directory:

* `Cargo.toml`: This file controls the configuration of the Rust project
* `clippy.toml`: This file configures the `clippy` static-analysis tool
* `rustfmt.toml`: This file configures the `rustfmt` code formatting tool

## Notes on Workspace Directories

Each of the algorithm directories (and the `common` directory) follows a basic
structure. Each has their own `Cargo.toml` file and a `src` directory. Within
the `src` directories is where the source code resides. In the case of the
`common/src` directory, there are three files. The algorithm directories each
have just a single file (`main.rs`).

### Directory `common`

This workspace has three files in the `src` subdirectory.

#### `input.rs`

This file is the first part of the framework for running the various
algorithms in a consistent fashion. This handles the reading of the data files
into Perl data.

There are three functions that are used directly by the runner-functions in the
`run.rs` module:

* `read_sequences`: Reads a sequences file
* `read_patterns`: Reads a patterns file
* `read_answers`: Reads the answers file

#### `lib.rs`

This file defines a linkable library of code in a Rust project. Here, it is
used to export the `input.rs` and `run.rs` modules for linkage.

#### `run.rs`

This file is the second part of the framework. It handles the running of a
given experiment. Four "runner" functions are provided:

* `run`: Runs a basic exact-matching algorithm
* `run_multi`: Runs a multi-pattern (exact) matching algorithm
* `run_approx`: Runs an approximate-matching algorithm

### Directory `aho_corasick`

The implementation of the Aho-Corasick algorithm:
<https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm>

### Directory `boyer_moore`

The implementation of the Boyer-Moore algorithm:
<https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm>

### Directory `dfa_gap`

The basic implementation of the DFA-Gap algorithm as described in the thesis.

### Directory `kmp`

The implementation of the Knuth-Morris-Pratt algorithm:
<https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm>

### Directory `regexp`

The implementation of the regular expression variant of the DFA-Gap algorithm.
This requires the [PCRE2](https://www.pcre.org/) library to compile and run,
and references the `pcre2` crate as well.

### Directory `shift_or`

The implementation of the Bitap ("Shift-Or") algorithm:
<https://en.wikipedia.org/wiki/Bitap_algorithm>
