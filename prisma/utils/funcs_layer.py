# --------------------------------------------------------------------------
def overwrite_row(orig, modf, i0, i1):
    # w_kernel = i1 - i0
    return orig[:i0] + modf[:i1-i0] + orig[i1:]


# --------------------------------------------------------------------------
def overlay_row(orig, modf, i0, i1):
    # w_kernel = i1 - i0
    middle = [
        m if m != ' ' else o \
        for o,m in zip(orig[i0:i1], modf[:i1-i0])
    ]
    if isinstance(orig, str): middle = ''.join(middle)
    return orig[:i0] + middle + orig[i1:]


# ------------------------------------------------------------------------------
