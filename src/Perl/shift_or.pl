#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use constant ASIZE => 128;
use constant WORD => 64;

use Run qw(run);

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

sub init_shift_or {
    my ($pattern) = @_;
    my $m = scalar @{$pattern};

    if ($m > WORD) {
        die 'shift_or: pattern size must be <= ' . WORD . "\n";
    }

    return [ calc_s_positions($pattern, $m) ];
}

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
