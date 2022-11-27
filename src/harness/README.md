# Harness Utility

This directory contains the harness code that was written to execute all the
experiments.

This is a C program that uses the
[RAPL](https://en.wikipedia.org/wiki/Running_average_power_limit) system that
Intel provides on some CPUs to measure the energy usage across the CPU package
during the execution of a given experiment.

It also measures running time of the whole program, the maximum memory-size
reached by the program, and runs for a specified number of iterations while
including the iteration number and success/failure result as well.

## The `subprocess.h` File

The file `subprocess.h` comes from the
[same-named](https://github.com/sheredom/subprocess.h) GitHub repository. It
_drastically_ simplified the process-handling necessary in this utility. Kudos
to the author for this piece of code.

## Notes on the Harness Code

The code here is heavily adapted from the repository
[Energy-Languages](https://github.com/greensoftwarelab/Energy-Languages), which
is the code behind the work detailed
[here](https://sites.google.com/view/energy-efficiency-languages) from the
paper "Energy Efficiency across Programming Languages: How does Energy, Time
and Memory Relate?" If this sort of research interests you, I strongly
recommend visiting their site and reading the paper (link available on the
site).

This harness is based specifically on the C code in the
[RAPL](https://github.com/greensoftwarelab/Energy-Languages/tree/master/RAPL)
sub-directory.
