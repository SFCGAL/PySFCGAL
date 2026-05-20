"""The `sfcgal` module is the main module of PySFCGAL.

It initially contained the definition of every geometry classes, plus some I/O
functions. It is kept in order to ensure the retrocompatibility of the API.

"""
import warnings

# API retrocompatibility
from pysfcgal import sfcgal_full_version, sfcgal_version
from pysfcgal.exceptions import DimensionError
from pysfcgal.geometry import (Axis, BufferType, CoordinateSequence, Geometry,
                               GeometryCollection, GeometrySequence,
                               LineString, MultiLineString, MultiPoint,
                               MultiPolygon, MultiSolid, Point, Polygon,
                               PolyhedralSurface, Solid, Tin, Triangle)

__all__ = [
    "Axis",
    "BufferType",
    "CoordinateSequence",
    "DimensionError",
    "Geometry",
    "GeometryCollection",
    "GeometrySequence",
    "LineString",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "MultiSolid",
    "Point",
    "Polygon",
    "PolyhedralSurface",
    "Solid",
    "Tin",
    "Triangle",
    "sfcgal_version",
    "sfcgal_full_version",
]

warnings.warn(
    "The pysfcgal.sfcgal module is deprecated, replace it with pysfcgal.geometry.",
    DeprecationWarning,
    stacklevel=2,
)
