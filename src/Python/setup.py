def read_two_ints(f):
    line = f.readline()

    return tuple(map(int, line.strip().split(" ")))


def read_sequences(file):
    with open(file, "r") as f:
        # Python does not need the second integer here.
        count, _ = read_two_ints(f)

        data = f.read().splitlines()

    if len(data) != count:
        raise Exception(f"Wrong number of data-lines in {file}")

    return data


def read_patterns(file):
    return read_sequences(file)


def read_answers(file):
    with open(file, "r") as f:
        # We need the second integer in this case.
        count, num_count = read_two_ints(f)

        data = f.read().splitlines()

    if len(data) != count:
        raise Exception(f"Wrong number of data-lines in {file}")

    data = list(map(lambda l: list(map(int, l.split(","))), data))
    for idx in range(len(data)):
        if len(data[idx]) != num_count:
            raise Exception(
                f"Data line {idx+1} has incorrect number of entries"
            )

    return data
