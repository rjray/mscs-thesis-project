#!/usr/bin/env perl

use 5.010;
use strict;
use warnings;
use lib qw(.);
use constant ASIZE => 128;
use constant FAIL => -1;

use Time::HiRes qw(gettimeofday tv_interval);

use Setup;

my @ALPHA_OFFSETS = qw(65 67 71 84);

sub add_goto_state {
    my $goto_fn = shift;

    push @{$goto_fn}, [(FAIL) x ASIZE];

    return;
}

sub enter_pattern {
    my ($pat, $idx, $goto_fn, $output_fn) = @_;
    my $len = scalar @{$pat};
    my $j = 0;
    my $state = 0;

    state $new_state = 0;

    while ($goto_fn->[$state][$pat->[$j]] != FAIL) {
        $state = $goto_fn->[$state][$pat->[$j]];
        $j++;
        if ($j == $len) {
            break;
        }
    }

    foreach my $p ($j..($len - 1)) {
        $new_state++;
        $goto_fn->[$state][$pat->[$p]] = $new_state;
        add_goto_state($goto_fn);
        push @{$output_fn}, {};
        $state = $new_state;
    }

    $output_fn->[$state]{$idx} = 1;

    return;
}

sub build_goto {
    my ($patterns, $goto_fn, $output_fn) = @_;

    # Set the initial values for state 0:
    add_goto_state($goto_fn);
    push @{$output_fn}, {};

    # Add each pattern in turn:
    my $idx = 0;
    for my $pat (@{$patterns}) {
        enter_pattern([ map { ord } split //, $pat ], $idx++, $goto_fn,
                      $output_fn);
    }

    # Set unused transitions in state 0 to point to state 0:
    foreach my $i (0..(ASIZE - 1)) {
        if ($goto_fn->[0][$i] == FAIL) {
            $goto_fn->[0][$i] = 0;
        }
    }

    return;
}

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
            $output_fn->[$s] = {
                %{$output_fn->[$s]},
                %{$output_fn->[$failure_fn[$s]]}
            };
        }
    }

    return \@failure_fn;
}

# Perform the Aho-Corasick algorithm against the given sequence. No pattern is
# passed in, as the machine of goto_fn/failure_fn/output_fn will handle all the
# patterns in a single pass.
#
# Instead of returning a single int, returns an array of ints as long as the
# number of patterns ($pattern_count).
sub aho_corasick {
    my ($sequence, $pattern_count, $goto_fn, $failure_fn, $output_fn) = @_;
    my @matches = (0) x $pattern_count;
    my $state = 0;

    for my $s (map { ord } split //, $sequence) {
        while ($goto_fn->[$state][$s] == FAIL) {
            $state = $failure_fn->[$state];
        }

        $state = $goto_fn->[$state][$s];
        for my $idx (keys %{$output_fn->[$state]}) {
            $matches[$idx]++;
        }
    }

    return \@matches;
}

# This is a customization of the runner function used for the single-pattern
# matching algorithms. This one sets up the structures needed for the A-C
# algorithm, then iterates over the sequences (since iterating over the patterns
# is not necessary).
#
# The return value is 0 if the experiment correctly identified all pattern
# instances in all sequences, and the number of misses otherwise.
sub run {
    my ($sequences_file, $patterns_file, $answers_file) = @_;
    my ($sequences_data, $patterns_data, $answers_data);

    if (! ($sequences_file && $patterns_file)) {
        die "Usage: $0 <sequences> <patterns> [ <answers> ]\n";
    }

    $sequences_data = read_sequences($sequences_file);
    $patterns_data = read_patterns($patterns_file);
    if ($answers_file) {
        $answers_data = read_answers($answers_file);
        if (@{$answers_data} != @{$patterns_data}) {
            die 'Count mismatch between patterns file and answers file';
        }
    }

    # Run it. First, prepare the data structures for the combined pattern that
    # will be used for matching. Then, for each sequence, try the combined
    # pattern against it. The aho_corasick() function will return an array of
    # integers for the count of matches of each pattern within the given
    # sequence. Report any mismatches (if we have answers data available).
    my $start_time = [ gettimeofday ];
    my $return_code = 0;

    my (@goto_fn, @output_fn);
    build_goto($patterns_data, \@goto_fn, \@output_fn);
    my $failure_fn = build_failure(\@goto_fn, \@output_fn);
    my $pat_count = scalar @{$patterns_data};

    foreach my $sequence (0..$#{$sequences_data}) {
        my $sequence_str = $sequences_data->[$sequence];
        my $matches = aho_corasick($sequence_str, $pat_count,
                                   \@goto_fn, $failure_fn, \@output_fn);

        if ($answers_data) {
            for my $pattern (0..$#{$patterns_data}) {
                if ($matches->[$pattern] !=
                    $answers_data->[$pattern][$sequence]) {
                    printf {*STDERR}
                        "Pattern %d mismatch against sequence %d (%d != %d)\n",
                        $pattern + 1, $sequence + 1, $matches->[$pattern],
                        $answers_data->[$pattern][$sequence];
                    $return_code++;
                }
            }
        }
    }

    # Note the end-time before doing anything else.
    my $elapsed = tv_interval($start_time);

    print "language: perl\nalgorithm: aho_corasick\n";
    printf "runtime: %.6f\n", $elapsed;

    return $return_code;
}

exit run(@ARGV);
