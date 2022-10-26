package Run;

use strict;
use warnings;
use lib qw(.);

use Exporter qw(import);
use Time::HiRes qw(gettimeofday tv_interval);

use Input;

our @EXPORT_OK = qw(run run_multi run_approx);

sub run {
    my ($init, $code, $name, @argv) = @_;
    my ($sequences_file, $patterns_file, $answers_file) = @argv;
    my ($sequences_data, $patterns_data, $answers_data);

    if (! ($sequences_file && $patterns_file)) {
        die "Usage: $0 <sequences> <patterns> [ <answers> ]\n";
    }

    $sequences_data = read_sequences($sequences_file);
    $patterns_data = read_patterns($patterns_file);
    if ($answers_file) {
        $answers_data = read_answers($answers_file);
        if (@{$answers_data} != @{$patterns_data}) {
            die 'Count mismatch between patterns file and answers file';
        }
    }

    my $start_time = [ gettimeofday ];
    my $return_code = 0;

    # Preprocess patterns and sequences, since all of the algorithms that use
    # this module need the same style of data.
    for my $pattern (@{$patterns_data}) {
        $pattern = [ map { ord } split //, $pattern ];
    }
    for my $sequence (@{$sequences_data}) {
        $sequence = [ map { ord } split //, $sequence ];
    }

    foreach my $pattern (0..$#{$patterns_data}) {
        my $pat_data = $init->($patterns_data->[$pattern]);

        foreach my $sequence (0..$#{$sequences_data}) {
            my $matches =
                $code->($pat_data, $sequences_data->[$sequence]);

            if ($answers_data &&
                ($matches != $answers_data->[$pattern][$sequence])) {
                printf {*STDERR}
                    "Pattern %d mismatch against sequence %d (%d != %d)\n",
                    $pattern + 1, $sequence + 1, $matches,
                    $answers_data->[$pattern][$sequence];
                $return_code++;
            }
        }
    }

    # Note the end-time before doing anything else.
    my $elapsed = tv_interval($start_time);

    print "language: perl\nalgorithm: $name\n";
    printf "runtime: %.6f\n", $elapsed;

    return $return_code;
}

# This is a customization of the runner function used for the single-pattern
# matching algorithms. This one sets up the structures needed for the A-C
# algorithm via a call to init-(), then iterates over just the sequences (since
# iterating over the patterns is not necessary).
#
# The return value is 0 if the experiment correctly identified all pattern
# instances in all sequences, and the number of misses otherwise.
sub run_multi {
    my ($init, $code, $name, @argv) = @_;
    my ($sequences_file, $patterns_file, $answers_file) = @argv;
    my ($sequences_data, $patterns_data, $answers_data);

    if (! ($sequences_file && $patterns_file)) {
        die "Usage: $0 <sequences> <patterns> [ <answers> ]\n";
    }

    $sequences_data = read_sequences($sequences_file);
    $patterns_data = read_patterns($patterns_file);
    if ($answers_file) {
        $answers_data = read_answers($answers_file);
        if (@{$answers_data} != @{$patterns_data}) {
            die 'Count mismatch between patterns file and answers file';
        }
    }

    my $start_time = [ gettimeofday ];
    my $return_code = 0;

    # Preprocess patterns and sequences, since all of the algorithms that use
    # this module need the same style of data.
    for my $pattern (@{$patterns_data}) {
        $pattern = [ map { ord } split //, $pattern ];
    }
    for my $sequence (@{$sequences_data}) {
        $sequence = [ map { ord } split //, $sequence ];
    }

    my $pat_data = $init->($patterns_data);

    foreach my $sequence (0..$#{$sequences_data}) {
        my $matches = $code->($pat_data, $sequences_data->[$sequence]);

        if ($answers_data) {
            for my $pattern (0..$#{$patterns_data}) {
                if ($matches->[$pattern] !=
                    $answers_data->[$pattern][$sequence]) {
                    printf {*STDERR}
                        "Pattern %d mismatch against sequence %d (%d != %d)\n",
                        $pattern + 1, $sequence + 1, $matches->[$pattern],
                        $answers_data->[$pattern][$sequence];
                    $return_code++;
                }
            }
        }
    }

    # Note the end-time before doing anything else.
    my $elapsed = tv_interval($start_time);

    print "language: perl\nalgorithm: $name\n";
    printf "runtime: %.6f\n", $elapsed;

    return $return_code;
}

sub run_approx {
    my ($init, $code, $name, @argv) = @_;
    my ($k, $sequences_file, $patterns_file, $answers_file) = @argv;
    my ($sequences_data, $patterns_data, $answers_data);

    if (! ($sequences_file && $patterns_file)) {
        die "Usage: $0 <k> <sequences> <patterns> [ <answers> ]\n";
    }

    $sequences_data = read_sequences($sequences_file);
    $patterns_data = read_patterns($patterns_file);
    if ($answers_file) {
        my $k_read;
        $answers_file = sprintf $answers_file, $k;
        $answers_data = read_answers($answers_file, \$k_read);
        if (@{$answers_data} != @{$patterns_data}) {
            die 'Count mismatch between patterns file and answers file';
        }
        if ($k != $k_read) {
            die "Mismatch in k values ($k vs $k_read)";
        }
    }

    my $start_time = [ gettimeofday ];
    my $return_code = 0;

    # Preprocess patterns and sequences, since all of the algorithms that use
    # this module need the same style of data.
    for my $pattern (@{$patterns_data}) {
        $pattern = [ map { ord } split //, $pattern ];
    }
    for my $sequence (@{$sequences_data}) {
        $sequence = [ map { ord } split //, $sequence ];
    }

    foreach my $pattern (0..$#{$patterns_data}) {
        my $pat_data = $init->($patterns_data->[$pattern], $k);

        foreach my $sequence (0..$#{$sequences_data}) {
            my $matches =
                $code->($pat_data, $sequences_data->[$sequence]);

            if ($answers_data &&
                ($matches != $answers_data->[$pattern][$sequence])) {
                printf {*STDERR}
                    "Pattern %d mismatch against sequence %d (%d != %d)\n",
                    $pattern + 1, $sequence + 1, $matches,
                    $answers_data->[$pattern][$sequence];
                $return_code++;
            }
        }
    }

    # Note the end-time before doing anything else.
    my $elapsed = tv_interval($start_time);

    print "language: perl\nalgorithm: $name($k)\n";
    printf "runtime: %.6f\n", $elapsed;

    return $return_code;
}

1;
