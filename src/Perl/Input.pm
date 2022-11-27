# Handle the reading and input of all the sequences/patterns/answers files over
# all of the Perl-based experiments.

package Input;

use strict;
use warnings;

use Exporter qw(import);

# Every user of this uses all three, so no need for @EXPORT_OK here.
our @EXPORT = qw(read_sequences read_patterns read_answers);

# Read the first line of an open filehandle, expecting it to be a list of
# numbers separated by spaces.
sub read_header {
    my $fh = shift;

    my $line = <$fh>;
    chomp $line;
    my @parts = split / /, $line;

    return @parts;
}

# Read the sequences data file. Gets the number of expected lines from the
# first line/header and checks that the correct number of lines were read after
# the header.
sub read_sequences {
    my $file = shift;
    my @data;

    if (open my $fh, q{<}, $file) {
        # Perl does not need the second integer here.
        my ($count) = read_header($fh);
        chomp(@data = <$fh>);
        close $fh;

        if (@data != $count) {
            my $read = scalar @data;
            die "Incorrect number of lines read from $file: $count/$read";
        }
    } else {
        die "Error opening $file for writing: $!";
    }

    return \@data;
}

# Read the patterns data file. This is the same format as the sequences file,
# so just thread through to read_patterns().
sub read_patterns {
    my $file = shift;

    return read_sequences($file);
}

# Read the answers data file. Here, the header is more meaningful; we need the
# second number for sanity-checking and we might need the third number as well.
# The third number is the value of `k` for the approximate-matching algorithms
# and will need to be checked against the `k` that was given on the command
# line.
sub read_answers {
    my ($file, $kref) = @_;
    my @data;

    if (open my $fh, q{<}, $file) {
        # We need the second integer in this case, and possibly a third.
        my ($count, $num_count, $k) = read_header($fh);
        if ($kref) {
            ${$kref} = $k;
        }

        chomp(@data = <$fh>);
        close $fh;

        if (@data != $count) {
            my $read = scalar @data;
            die "Incorrect number of lines read from $file: $count/$read";
        }

        @data = map { [ split /,/ ] } @data;
        foreach my $idx (0..$#data) {
            if (@{$data[$idx]} != $num_count) {
                $idx++;
                die "Data line $idx has incorrect number of entries";
            }
        }
    } else {
        die "Error opening $file for writing: $!";
    }

    return \@data;
}

1;
