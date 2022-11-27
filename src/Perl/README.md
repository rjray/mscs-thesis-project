# Perl Source Code

Here you will find the source code for the Perl experiments. It is structured
as with the other languages, with a controlling `Makefile` and framework code.

## File `Input.pm`

This file is the first part of the framework for running the various
algorithms in a consistent fashion. This handles the reading of the data files
into Perl data.

There are three functions that are used directly by the runner-functions in the
`Run.pm` module:

* `read_sequences`: Reads a sequences file
* `read_patterns`: Reads a patterns file
* `read_answers`: Reads the answers file

## File `Run.pm`

This file is the second part of the framework. It handles the running of a
given experiment. Four "runner" functions are provided:

* `run`: Runs a basic exact-matching algorithm
* `run_multi`: Runs a multi-pattern (exact) matching algorithm
* `run_approx`: Runs an approximate-matching algorithm
* `run_approx_raw`: Runs an approximate-matching algorithm without any pre-processing of the input data (done in the regular expression algorithm)

## File `aho_corasick.pl`

The implementation of the Aho-Corasick algorithm:
<https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm>

## File `boyer_moore.pl`

The implementation of the Boyer-Moore algorithm:
<https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm>

## File `dfa_gap.pl`

The basic implementation of the DFA-Gap algorithm as described in the thesis.

## File `kmp.pl`

The implementation of the Knuth-Morris-Pratt algorithm:
<https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm>

## File `regexp.pl`

The implementation of the regular expression variant of the DFA-Gap algorithm.

## File `shift_or.pl`

The implementation of the Bitap ("Shift-Or") algorithm:
<https://en.wikipedia.org/wiki/Bitap_algorithm>
