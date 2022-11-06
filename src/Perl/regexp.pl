#!/usr/bin/env perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;

use Run qw(run_approx_raw);

sub init_regexp {
    my ($pattern, $k) = @_;
    my @pattern = split //, $pattern;
    my $expr = shift @pattern;

    foreach my $char (@pattern) {
        $expr .= sprintf '[^%s]{0,%d}%s', $char, $k, $char;
    }
    $expr = qr/(?=$expr)/;

    return [ $expr ];
}

sub regexp {
    my ($pat_data, $sequence) = @_;
    my ($expr) = @{$pat_data};

    my @matches = $sequence =~ /$expr/g;

    return scalar @matches;
}

exit run_approx_raw(\&init_regexp, \&regexp, 'regexp', \@ARGV);
