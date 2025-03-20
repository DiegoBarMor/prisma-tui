import warnings

# ------------------------------------------------------------------------------
def apply_mask(idxs, mat, char):
    mat_out = tuple(map(
        lambda idx, arr: tuple(filter(
            lambda tup: tup[1] == char,
            zip(idx, arr)
        )),
        idxs, mat
    ))
    return tuple(tuple(n[0] for n in arr) for arr in mat_out if arr)


# ------------------------------------------------------------------------------
def all_elements_equal(iterable):
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(first == rest for rest in iterator)


# ------------------------------------------------------------------------------
def is_sequential(iterable):
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(i == element for i,element in enumerate(iterator, start = first + 1))


# ------------------------------------------------------------------------------
def mosaic(layout):
    print(layout); print()

    if not layout:
        warnings.warn("Empty layout")
        return False

    rows = layout.split('\n')
    cols = tuple(zip(*rows))

    row_lenghts = set(map(len, rows))
    if len(row_lenghts) != 1:
        raise ValueError("Not all mosaic rows have the same lenght.")

    xidxs = tuple(range(len(row)) for row in rows)
    yidxs = tuple(range(len(col)) for col in cols)


    chars = set(layout)
    if '\n' in chars: chars.remove('\n')

    for char in chars:
        masked_xidxs = apply_mask(xidxs, rows, char)
        masked_yidxs = apply_mask(yidxs, cols, char)

        if not all_elements_equal(masked_xidxs):
            raise ValueError(f"Not all rows for char '{char}' have the same length.")

        if not all_elements_equal(masked_yidxs):
            raise ValueError(f"Not all columns for char '{char}' have the same length.")

        if not is_sequential(masked_xidxs[0]):
            raise ValueError(f"Rows of char '{char}' are interrupted.")

        if not is_sequential(masked_yidxs[0]):
            raise ValueError(f"Columns of char '{char}' are interrupted.")

        print(char, "masked_xidxs:", masked_xidxs)
        print(char, "masked_yidxs:", masked_yidxs)

    return True

        # print(*zip(rows, mask(rows, 'a'))    , sep="\n")


# ------------------------------------------------------------------------------
