#!/usr/bin/env perl

use strict;
use warnings;
use lib qw(.);
use constant ASIZE => 128;

use Run qw(run);

# Surprisingly not in any of the core Perl modules:
sub max {
    my ($a, $b) = @_;

    return ($b > $a) ? $b : $a;
}

sub calc_bad_char {
    my ($pat, $m, $bad_char) = @_;

    foreach my $i (0..($m - 2)) {
        $bad_char->[$pat->[$i]] = $m - 1 - $i;
    }

    return;
}

sub calc_suffixes {
    my ($pat, $m, $suffix_list) = @_;
    $suffix_list->[$m - 1] = $m;

    my $f = 0;
    my $g = $m - 1;
    foreach my $i (reverse 0..($m - 2)) {
        if ($i > $g && $suffix_list->[$i + $m - 1 - $f] < $i - $g) {
            $suffix_list->[$i] = $suffix_list->[$i + $m - 1 - $f];
        } else {
            if ($i < $g) {
                $g = $i;
            }
            $f = $i;
            while ($g >= 0 && $pat->[$g] == $pat->[$g + $m - 1 - $f]) {
                $g--;
            }
            $suffix_list->[$i] = $f - $g;
        }
    }

    return;
}

sub calc_good_suffix {
    my ($pat, $m, $good_suffix) = @_;
    my @suffixes = (0) x $m;

    calc_suffixes($pat, $m, \@suffixes);

    my $j = 0;
    my $i = $m - 1;
    while ($i >= -1) {
        if ($i == -1 || $suffixes[$i] == $i + 1) {
            while ($j < $m - 1 - $i) {
                if ($good_suffix->[$j] == $m) {
                    $good_suffix->[$j] = $m - 1 - $i;
                }

                $j++;
            }
        }

        $i--;
    }

    foreach my $i (0..($m - 2)) {
        $good_suffix->[$m - 1 - $suffixes[$i]] = $m - 1 - $i;
    }

    return;
}

sub boyer_moore {
    my ($pattern, $m, $sequence, $n) = @_;
    my @pat = map { ord } split //, $pattern;
    push @pat, 0;
    my @seq = map { ord } split //, $sequence;
    my $matches = 0;

    my @good_suffix = ($m) x $m;
    my @bad_char = ($m) x ASIZE;

    calc_good_suffix(\@pat, $m, \@good_suffix);
    calc_bad_char(\@pat, $m, \@bad_char);

    my $j = 0;
    while ($j <= $n - $m) {
        my $i = $m - 1;
        while ($i >= 0 && $pat[$i] == $seq[$i + $j]) {
            $i--;
        }
        if ($i < 0) {
            $matches++;
            $j += $good_suffix[0];
        } else {
            $j += max($good_suffix[$i], $bad_char[$seq[$i + $j]] - $m + 1 + $i);
        }
    }

    return $matches;
}

exit run(\&boyer_moore, 'boyer_moore', @ARGV);
