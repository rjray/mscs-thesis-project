#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;

use Run qw(run);

# Initialize the jump-table that KMP uses:
sub make_next_table {
    my ($pat, $m, $next_table) = @_;

    my $i = 0;
    my $j = $next_table->[0] = -1;

    while ($i < $m) {
        while ($j > -1 && $pat->[$i] != $pat->[$j]) {
            $j = $next_table->[$j];
        }
        $i++;
        $j++;
        if ($pat->[$i] == $pat->[$j]) {
            $next_table->[$i] = $next_table->[$j];
        } else {
            $next_table->[$i] = $j;
        }
    }

    return;
}

sub init_kmp {
    my ($pattern, $m) = @_;
    my $pat = [ @{$pattern}, 0 ];
    my @next_table = (0) x ($m + 1);

    make_next_table($pat, $m, \@next_table);

    return [ $pat, \@next_table ];
}

sub kmp {
    my ($pat_data, $m, $sequence, $n) = @_;
    my ($pat, $next_table) = @{$pat_data};
    my $matches = 0;

    my ($i, $j) = (0, 0);

    while ($j < $n) {
        while ($i > -1 && $pat->[$i] != $sequence->[$j]) {
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

exit run(\&init_kmp, \&kmp, 'kmp', @ARGV);
