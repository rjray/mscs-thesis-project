#!/usr/bin/env perl

# This is the implementation of the Shift-Or (Bitap) algorithm for Perl. It is
# adapted from the C code, which is based heavily on the code given in chapter 5
# of the book, "Handbook of Exact String-Matching Algorithms," by Christian
# Charras and Thierry Lecroq.

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use constant ASIZE => 128;
use constant WORD => 64;

use Run qw(run);

# Calculate the s_positions table from the pattern characters. In this case, the
# pattern is already converted from characters to integers. This also calculates
# the value of $lim, and returns both elements.
sub calc_s_positions {
    my ($pat, $m) = @_;
    my ($i, $j, $lim);
    my @s_positions = (~0) x ASIZE;

    $i = 0;
    $lim = 0;
    $j = 1;
    foreach my $i (0..($m - 1)) {
        $s_positions[$pat->[$i]] &= ~$j;
        $lim |= $j;

        $j <<= 1;
    }
    $lim = ~($lim >> 1);

    return $lim, \@s_positions;
}

# Initialize the pattern representation for use by the `shift_or` function on
# each sequence.
sub init_shift_or {
    my ($pattern) = @_;
    my $m = scalar @{$pattern};

    if ($m > WORD) {
        die 'shift_or: pattern size must be <= ' . WORD . "\n";
    }

    return [ calc_s_positions($pattern, $m) ];
}

# Run the Shift-Or algorithm on the given sequence, using the packed pattern
# data.
sub shift_or {
    my ($pat_data, $seq) = @_;
    my ($lim, $s_positions) = @{$pat_data};
    my $matches = 0;

    # Get the size of the sequence. Pattern size is not needed here.
    my $n = scalar @{$seq};

    my $state = ~0;
    foreach my $j (0..($n - 1)) {
        $state = ($state << 1) | $s_positions->[$seq->[$j]];
        if ($state < $lim) {
            $matches++;
        }
    }

    return $matches;
}

exit run(\&init_shift_or, \&shift_or, 'shift_or', \@ARGV);
