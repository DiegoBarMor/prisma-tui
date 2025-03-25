# --------------------------------------------------------------------------
def np2str(arr, value_map):
    return [''.join(value_map[i] for i in row) for row in arr]


# --------------------------------------------------------------------------
def np2list(arr, value_map):
    return [[value_map[i] for i in row] for row in arr]


# --------------------------------------------------------------------------
def overwrite_row(orig, modf, i0, i1):
    w_kernel = i1 - i0
    return orig[:i0] + modf[:w_kernel] + orig[i1:]


# --------------------------------------------------------------------------
def overlay_row(orig, modf, i0, i1):
    w_kernel = i1 - i0
    middle = [
        m if m != ' ' else o \
        for o,m in zip(orig[i0:i1], modf[:w_kernel])
    ]
    if isinstance(orig, str): middle = ''.join(middle)
    return orig[:i0] + middle + orig[i1:]


# ------------------------------------------------------------------------------
