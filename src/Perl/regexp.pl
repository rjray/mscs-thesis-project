#!/usr/bin/env perl

# This is the regular expression variant of the DFA-Gap algorithm. Unlike the
# various exact-matching algorithms and the basic DFA-Gap itself, this was
# written first in Perl, then Python, and then ported to the compiled languages.

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;

use Run qw(run_approx_raw);

# Initialize the pattern data for the algorithm itself. Here, we have a great
# advantage over the compiled languages in that regex are built in and can be
# passed around as objects on the stack without any special libraries or tools.
sub init_regexp {
    my ($pattern, $k) = @_;
    my @pattern = split //, $pattern;
    my $expr = shift @pattern;

    foreach my $char (@pattern) {
        $expr .= sprintf '[^%s]{0,%d}%s', $char, $k, $char;
    }
    $expr = qr/(?=($expr))/;

    return [ $expr ];
}

# Perform the regular expression variant algorithm. It really is just the one
# line, for Perl.
sub regexp {
    my ($pat_data, $sequence) = @_;
    my ($expr) = @{$pat_data};

    my @matches = $sequence =~ /$expr/g;

    return scalar @matches;
}

exit run_approx_raw(\&init_regexp, \&regexp, 'regexp', \@ARGV);
