# Changelog

## [0.1.0] - 2025-05-30
- Initial upload to PyPI of a preliminary **Prisma TUI**.

## [0.1.1] - 2025-06-01
- Added README and some documentation.

## [0.2.0] - 2025-10-07
- Renamed the package from `prisma` into `prisma-tui` to avoid name conflicts with other packages using the word "prisma".

## [0.2.1]
- Attempted to reduce input lag by exhausting repeated keys in `BackendCurses._get_key`.
- Palettes can now be loaded directly from a dictionary instead of a JSON file.
- Package no longer nested inside a `src/` folder.
