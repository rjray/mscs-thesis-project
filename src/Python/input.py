# This is the input module for the experiments. It handles reading of data
# and returning the content in Python structures.

# Read the first line of the open filehandle `f` and parse it as a set of
# space-separated integers.
def read_header(f):
    line = f.readline()

    return list(map(int, line.strip().split(" ")))


# Read the given filename as a file of sequence data. The first line should be
# integers specifying the number of data lines to read. The rest of the lines
# are the data. Check that the number of lines is correct.
def read_sequences(file):
    with open(file, "r") as f:
        # Python does not need the second integer here.
        count = read_header(f)[0]

        data = f.read().splitlines()

    if len(data) != count:
        raise Exception(f"Wrong number of data-lines in {file}")

    return data


# Read the given filename as a file of pattern data. The structure is the same
# as sequences data, so this just threads through to the previous function.
def read_patterns(file):
    return read_sequences(file)


# Read the given filename as a file of answers data. If `need_k` is True, then
# this is an approximate-match answers set and the third parameter of the
# header line should also be returned.
def read_answers(file, need_k=False):
    with open(file, "r") as f:
        numbers = read_header(f)

        if need_k:
            # We need all three numbers in this case.
            count, num_count, k = numbers
        else:
            # We need just the first two in this case.
            count, num_count = numbers
            k = None

        data = f.read().splitlines()

    if len(data) != count:
        raise Exception(f"Wrong number of data-lines in {file}")

    data = list(map(lambda l: list(map(int, l.split(","))), data))
    for idx in range(len(data)):
        if len(data[idx]) != num_count:
            raise Exception(
                f"Data line {idx+1} has incorrect number of entries"
            )

    if need_k:
        return data, k
    else:
        return data
