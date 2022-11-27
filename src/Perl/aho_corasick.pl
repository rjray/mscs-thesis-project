#!/usr/bin/env perl

# This is the implementation of the Aho-Corasick algorithm, in Perl. This was
# not adapted from existing code (as the C versions of KMP, Boyer-Moore and
# Shift-Or were), but from the C code that was written directly from the
# published algorithm in the original paper.

use 5.010;
use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use constant ASIZE => 128;
use constant FAIL => -1;

use List::Util qw(uniq);

use Run qw(run_multi);

my @ALPHA_OFFSETS = qw(65 67 71 84);

# Create a new state for the goto_fn part of the DFA.
sub add_goto_state {
    my $goto_fn = shift;

    push @{$goto_fn}, [(FAIL) x ASIZE];

    return;
}

# Add one pattern to the given goto_fn and record its index in the output_fn.
sub enter_pattern {
    my ($pat, $idx, $goto_fn, $output_fn) = @_;
    my $len = scalar @{$pat};
    my $j = 0;
    my $state = 0;

    state $new_state = 0;

    while ($goto_fn->[$state][$pat->[$j]] != FAIL) {
        $state = $goto_fn->[$state][$pat->[$j]];
        $j++;
    }

    foreach my $p ($j..($len - 1)) {
        $new_state++;
        $goto_fn->[$state][$pat->[$p]] = $new_state;
        add_goto_state($goto_fn);
        push @{$output_fn}, [];
        $state = $new_state;
    }

    push @{$output_fn->[$state]}, $idx;

    return;
}

# This will completely build goto_fn, but only partially build the output_fn.
# It initializes the two, then adds each pattern in turn to goto_fn.
sub build_goto {
    my ($patterns, $goto_fn, $output_fn) = @_;

    # Set the initial values for state 0:
    add_goto_state($goto_fn);
    push @{$output_fn}, {};

    # Add each pattern in turn:
    my $idx = 0;
    foreach my $pat (@{$patterns}) {
        enter_pattern($pat, $idx++, $goto_fn, $output_fn);
    }

    # Set unused transitions in state 0 to point to state 0:
    foreach my $i (0..(ASIZE - 1)) {
        if ($goto_fn->[0][$i] == FAIL) {
            $goto_fn->[0][$i] = 0;
        }
    }

    return;
}

# Build failure_fn, and complete the construction of output_fn.
sub build_failure {
    my ($goto_fn, $output_fn) = @_;
    my @failure_fn = ();
    my @queue = ();

    # The failure function should be the same length as goto_fn.
    $#failure_fn = $#{$goto_fn};

    # The queue starts out empty. Set it to be all states reachable from state
    # 0 and set failure(state) for those states to be 0.
    foreach my $i (@ALPHA_OFFSETS) {
        my $state = $goto_fn->[0][$i];
        if ($state == 0) {
            next;
        }

        push @queue, $state;
        $failure_fn[$state] = 0;
    }

    # This uses some single-letter variable names that match the published
    # algorithm. Their mnemonic isn't clear, or else I'd use more meaningful
    # names.
    while (@queue) {
        my $r = shift @queue;
        foreach my $a (@ALPHA_OFFSETS) {
            my $s = $goto_fn->[$r][$a];
            if ($s == FAIL) {
                next;
            }

            push @queue, $s;
            my $state = $failure_fn[$r];
            while ($goto_fn->[$state][$a] == FAIL) {
                $state = $failure_fn[$state];
            }
            $failure_fn[$s] = $goto_fn->[$state][$a];
            $output_fn->[$s] =
                [ uniq @{$output_fn->[$s]}, @{$output_fn->[$failure_fn[$s]]}];
        }
    }

    return \@failure_fn;
}

# Initialize the Aho-Corasick structure that will be passed to the main routine
# for each target sequence being matched against.
sub init_aho_corasick {
    my $patterns = shift;
    my $pattern_count = scalar @{$patterns};

    my (@goto_fn, @output_fn);
    build_goto($patterns, \@goto_fn, \@output_fn);
    my $failure_fn = build_failure(\@goto_fn, \@output_fn);

    return [ $pattern_count, \@goto_fn, $failure_fn, \@output_fn];
}

# Perform the Aho-Corasick algorithm against the given sequence. No pattern is
# passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
# patterns in a single pass.
#
# Instead of returning a single int, returns an array of ints as long as the
# number of patterns ($pattern_count).
sub aho_corasick {
    my ($pat_data, $sequence) = @_;
    # Unpack $pat_data
    my ($pattern_count, $goto_fn, $failure_fn, $output_fn) = @{$pat_data};

    my @matches = (0) x $pattern_count;
    my $state = 0;

    foreach my $s (@{$sequence}) {
        while ($goto_fn->[$state][$s] == FAIL) {
            $state = $failure_fn->[$state];
        }

        $state = $goto_fn->[$state][$s];
        foreach my $idx (@{$output_fn->[$state]}) {
            $matches[$idx]++;
        }
    }

    return \@matches;
}

exit run_multi(\&init_aho_corasick, \&aho_corasick, 'aho_corasick', \@ARGV);
