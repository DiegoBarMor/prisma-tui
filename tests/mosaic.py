import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder

from prisma.utils.mosaic import mosaic

################################################################################
if __name__ == "__main__":
    layouts = dict(
        empty = '',
        row_clean = '\n'.join((
            "aaab",
        )),
        row_bad = '\n'.join((
            "axab",
        )),
        col_clean = '\n'.join((
            "a",
            "a",
            "c",
        )),
        col_bad = '\n'.join((
            "a",
            "x",
            "a",
            "c",
        )),
        box_clean = '\n'.join((
            "ltttt",
            "laaab",
            "laaab",
            "lcddd",
        )),
        box_missing_char = '\n'.join((
            "ltttt",
            "laaab",
            "laaa",
            "lcddd",
        )),
        box_bad_corner = '\n'.join((
            "ltttt",
            "laaab",
            "laaxb",
            "lcddd",
        )),
        box_bad_row = '\n'.join((
            "ltttt",
            "laaab",
            "lxxxb",
            "laaab",
            "lcddd",
        )),
        box_bad_col = '\n'.join((
            "ltttt",
            "laxab",
            "laxab",
            "lcddd",
        )),
        box_bad_interior = '\n'.join((
            "ltttt",
            "laaab",
            "laxab",
            "laaab",
            "lcddd",
        )),
    )

    for k, v in layouts.items():
        print("------------------", k)
        try:
            completed = mosaic(v)
        except ValueError as e:
            print("XXX", e)
        else:
            if completed: print("... Valid layout")
        print()


################################################################################
