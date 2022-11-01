#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use constant ASIZE => 128;
use constant FAIL => -1;

use Run qw(run_approx);

my @ALPHABET = qw(65 67 71 84);

sub create_dfa {
    my ($pattern, $m, $k) = @_;

    # We know that the number of states will be 1 + m + k(m - 1).
    my $max_states = 1 + $m + $k * ($m - 1);

    # Allocate the DFA.
    my @dfa;
    foreach my $i (1..$max_states) {
        push @dfa, [(FAIL) x ASIZE];
    }

    # Start building the DFA. Start with state 0 and iterate through the
    # characters of `pattern`.

    # First step: Set d(0, p_0) = state(1)
    $dfa[0][$pattern->[0]] = 1;

    # Start `state` and `new_state` both at 1
    my $state = 1;
    my $new_state = 1;

    # Loop over remaining `pattern` (index 1 to the end). Because we know the
    # size of the DFA, there is no need to initialize each new state, that's
    # been done already.
    foreach my $char (@{$pattern}[1..$#{$pattern}]) {
        $new_state++;
        $dfa[$state][$char] = $new_state;
        my $last_state = $state;
        foreach my $j (1..$k) {
            # For each of 1..k, we start a new state for which `char` maps to
            # `new_state`.
            $dfa[$new_state + $j][$char] = $new_state;
            foreach my $n (@ALPHABET) {
                if ($n != $char) {
                    $dfa[$last_state][$n] = $new_state + $j;
                }
            }
            $last_state = $new_state + $j;
        }
        $state = $new_state;
        $new_state += $k;
    }

    my $terminal = $state;
    return \@dfa, $terminal;
}

sub init_dfa_gap {
    my ($pattern, $k) = @_;
    my $m = scalar @{$pattern};

    my ($dfa, $terminal) = create_dfa($pattern, $m, $k);

    return [ $dfa, $terminal, $m ];
}

sub dfa_gap {
    my ($pat_data, $sequence) = @_;
    my ($dfa, $terminal, $m) = @{$pat_data};

    my $matches = 0;
    my $n = scalar @{$sequence};

    my $end = $n - $m;
    foreach my $i (0..$end) {
        my $state = 0;
        my $ch = 0;

        while (($i + $ch) < $n &&
               $dfa->[$state][$sequence->[$i + $ch]] != FAIL) {
            $state = $dfa->[$state][$sequence->[$i + $ch++]];
        }

        if ($state == $terminal) {
            $matches++;
        }
    }

    return $matches;
}

exit run_approx(\&init_dfa_gap, \&dfa_gap, 'dfa_gap', \@ARGV);
