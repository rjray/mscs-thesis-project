#!/bin/bash

find C C++ Perl Python Rust \
    -name \*.[ch] -o -name \*.[ch]pp -o -name \*.p[lm] -o -name \*.py -o \
    -name \*.rs \
    | sort | xargs sloc -f csv -d -a pm=pl
