package Setup;

use strict;
use warnings;

use Exporter qw(import);

our @EXPORT = qw(read_sequences read_patterns read_answers);

sub read_two_ints {
    my $fh = shift;

    my $line = <$fh>;
    chomp $line;
    my @parts = split / /, $line;

    return @parts;
}

sub read_sequences {
    my $file = shift;
    my @data;

    if (open my $fh, q{<}, $file) {
        # Perl does not need the second integer here.
        my ($count) = read_two_ints($fh);
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

sub read_patterns {
    my $file = shift;

    return read_sequences($file);
}

sub read_answers {
    my $file = shift;
    my @data;

    if (open my $fh, q{<}, $file) {
        # We need the second integer in this case.
        my ($count, $num_count) = read_two_ints($fh);
        chomp(@data = <$fh>);
        close $fh;

        if (@data != $count) {
            my $read = scalar @data;
            die "Incorrect number of lines read from $file: $count/$read";
        }

        @data = map { [ split /,/ ] } @data;
        for my $idx (0..$#data) {
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
