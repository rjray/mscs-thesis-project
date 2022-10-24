def read_header(f):
    line = f.readline()

    return list(map(int, line.strip().split(" ")))


def read_sequences(file):
    with open(file, "r") as f:
        # Python does not need the second integer here.
        count = read_header(f)[0]

        data = f.read().splitlines()

    if len(data) != count:
        raise Exception(f"Wrong number of data-lines in {file}")

    return data


def read_patterns(file):
    return read_sequences(file)


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
