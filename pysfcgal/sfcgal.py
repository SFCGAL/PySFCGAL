"""The `sfcgal` module is the main module of PySFCGAL.

It initially contained the definition of every geometry classes, plus some I/O
functions. It is kept in order to ensure the retrocompatibility of the API.

"""
import warnings

# API retrocompatibility
from pysfcgal import sfcgal_full_version, sfcgal_version
from pysfcgal.exceptions import DimensionError
from pysfcgal.geometry import (BufferType, CoordinateSequence, Geometry,
                               GeometryCollection, GeometrySequence,
                               LineString, MultiLineString, MultiPoint,
                               MultiPolygon, MultiSolid, Point, Polygon,
                               PolyhedralSurface, Solid, Tin, Triangle)
from pysfcgal.vector import UNIT_X, UNIT_Y, UNIT_Z, Vector3D

__all__ = [
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
    "UNIT_X",
    "UNIT_Y",
    "UNIT_Z",
    "Vector3D",
    "sfcgal_version",
    "sfcgal_full_version",
]

warnings.warn(
    "The pysfcgal.sfcgal module is deprecated, replace it with pysfcgal.geometry.",
    DeprecationWarning,
    stacklevel=2,
)
