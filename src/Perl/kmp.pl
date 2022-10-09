#!/usr/bin/env perl

use strict;
use warnings;
use lib qw(.);

use Run qw(run);

# Initialize the jump-table that KMP uses:
sub init_kmp {
    my ($pat, $m, $next_table) = @_;

    my $i = 0;
    my $j = $next_table->[0] = -1;

    while ($i < $m) {
        while ($j > -1 && $pat->[$i] ne $pat->[$j]) {
            $j = $next_table->[$j];
        }
        $i++;
        $j++;
        if ($pat->[$i] eq $pat->[$j]) {
            $next_table->[$i] = $next_table->[$j];
        } else {
            $next_table->[$i] = $j;
        }
    }

    return;
}

sub kmp {
    my ($pattern, $m, $sequence, $n) = @_;
    my @pat = split //, $pattern;
    push @pat, "\0";
    my @seq = split //, $sequence;
    my $matches = 0;
    my @next_table = (0) x ($m + 1);

    init_kmp(\@pat, $m, \@next_table);
    my ($i, $j) = (0, 0);

    while ($j < $n) {
        while ($i > -1 && $pat[$i] ne $seq[$j]) {
            $i = $next_table[$i];
        }
        $i++;
        $j++;
        if ($i >= $m) {
            $matches++;
            $i = $next_table[$i]
        }
    }

    return $matches;
}

exit run(\&kmp, 'kmp', @ARGV);
