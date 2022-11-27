# C Source Code

Here you will find the C experiments' source code. It is structured like the
other languages are, with a controlling `Makefile` and framework code.

## Files `input.c` and `input.h`

These files are the first part of the framework for running the various
algorithms in a consistent fashion. These specific files handle the reading of
the data files into dynamically-allocated memory.

There are three functions that are used directly by the runner-functions in the
`run.c` module:

* `read_sequences`: Reads a sequences file
* `read_patterns`: Reads a patterns file
* `read_answers`: Reads the answers file

## Files `run.c` and `run.h`

These files are the second part of the framework. They handle the running of a
given experiment. Three "runner" functions are provided:

* `run`: Runs a basic exact-matching algorithm
* `run_multi`: Runs a multi-pattern (exact) matching algorithm
* `run_approx`: Runs an approximate-matching algorithm

## File `aho_corasick.c`

The implementation of the Aho-Corasick algorithm:
<https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm>

## File `boyer_moore.c`

The implementation of the Boyer-Moore algorithm:
<https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm>

## File `dfa_gap.c`

The basic implementation of the DFA-Gap algorithm as described in the thesis.

## File `kmp.c`

The implementation of the Knuth-Morris-Pratt algorithm:
<https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm>

## File `regexp.c`

The implementation of the regular expression variant of the DFA-Gap algorithm.
This requires the [PCRE2](https://www.pcre.org/) library to compile and run.

## File `shift_or.c`

The implementation of the Bitap ("Shift-Or") algorithm:
<https://en.wikipedia.org/wiki/Bitap_algorithm>
