"""PySFCGAL specific exceptions."""


class DimensionError(Exception):
    """Indicates a dimension error, e.g. requesting for the Z coordinates in
    a 2D-point."""

    pass
