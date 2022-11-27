#!/usr/bin/env perl

# This is the Perl implementation of the Knuth-Morris-Pratt algorithm. It is
# adapted from the C implementation, which itself is based heavily on the code
# given in chapter 7 of the book, "Handbook of Exact String-Matching
# Algorithms," by Christian Charras and Thierry Lecroq.

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;

use Run qw(run);

# Initialize the jump-table that KMP uses:
sub make_next_table {
    my ($pat, $m) = @_;
    my @next_table = (0) x ($m + 1);

    my $i = 0;
    my $j = $next_table[0] = -1;

    while ($i < $m) {
        while ($j > -1 && $pat->[$i] != $pat->[$j]) {
            $j = $next_table[$j];
        }
        $i++;
        $j++;
        if ($pat->[$i] == $pat->[$j]) {
            $next_table[$i] = $next_table[$j];
        } else {
            $next_table[$i] = $j;
        }
    }

    return \@next_table;
}

# Set up the packed pattern representation that will be passed to each call of
# `kmp`.
sub init_kmp {
    my ($pattern) = @_;
    my $m = scalar @{$pattern};
    my $pat = [ @{$pattern}, 0 ];

    return [ $pat, make_next_table($pat, $m) ];
}

# Run the Knuth-Morris-Pratt algorithm on the sequence given with the packed
# pattern data given. Returns the number of matches found.
sub kmp {
    my ($pat_data, $seq) = @_;
    my ($pat, $next_table) = @{$pat_data};

    my $matches = 0;
    my ($i, $j) = (0, 0);

    # Get the sizes of the pattern and the sequence. Account for the sentinel
    # character added to the pattern.
    my $m = scalar @{$pat} - 1;
    my $n = scalar @{$seq};

    while ($j < $n) {
        while ($i > -1 && $pat->[$i] != $seq->[$j]) {
            $i = $next_table->[$i];
        }
        $i++;
        $j++;
        if ($i >= $m) {
            $matches++;
            $i = $next_table->[$i]
        }
    }

    return $matches;
}

exit run(\&init_kmp, \&kmp, 'kmp', \@ARGV);
