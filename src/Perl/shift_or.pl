#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use constant ASIZE => 128;
use constant WORD => 64;

use Run qw(run);

sub calc_s_positions {
    my ($pat, $m, $s_positions) = @_;
    my ($i, $j, $lim);

    $i = 0;
    $lim = 0;
    $j = 1;
    while ($i < $m) {
        $s_positions->[$pat->[$i]] &= ~$j;
        $lim |= $j;

        $i++;
        $j <<= 1;
    }
    $lim = ~($lim >> 1);

    return $lim;
}

sub init_shift_or {
    my ($pattern, $m) = @_;

    if ($m > WORD) {
        die 'shift_or: pattern size must be <= ' . WORD . "\n";
    }

    my @s_positions = (~0) x ASIZE;

    my $lim = calc_s_positions($pattern, $m, \@s_positions);

    return [ $pattern, $lim, \@s_positions ];
}

sub shift_or {
    my ($pat_data, $m, $seq, $n) = @_;
    my (undef, $lim, $s_positions) = @{$pat_data};
    my $matches = 0;

    my $state = ~0;
    foreach my $j (0..($n - 1)) {
        $state = ($state << 1) | $s_positions->[$seq->[$j]];
        if ($state < $lim) {
            $matches++;
        }
    }

    return $matches;
}

exit run(\&init_shift_or, \&shift_or, 'shift_or', @ARGV);
