#!/usr/bin/env perl

use strict;
use warnings;
use lib qw(.);
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

sub shift_or {
    my ($pattern, $m, $sequence, $n) = @_;
    my @pat = map { ord } split //, $pattern;
    push @pat, 0;
    my @seq = map { ord } split //, $sequence;
    my $matches = 0;

    if ($m > WORD) {
        die 'shift_or: pattern size must be <= ' . WORD . "\n";
    }

    my @s_positions = (~0) x ASIZE;

    my $lim = calc_s_positions(\@pat, $m, \@s_positions);

    my $state = ~0;
    foreach my $j (0..($n - 1)) {
        $state = ($state << 1) | $s_positions[$seq[$j]];
        if ($state < $lim) {
            $matches++;
        }
    }

    return $matches;
}

exit run(\&shift_or, 'shift_or', @ARGV);
