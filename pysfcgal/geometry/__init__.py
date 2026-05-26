"""PySFCGAL Geometry submodule."""

from pysfcgal.geometry.buffer import BufferType
from pysfcgal.geometry.collection import (GeometryCollection, GeometrySequence,
                                          MultiLineString, MultiPoint,
                                          MultiPolygon, MultiSolid)
from pysfcgal.geometry.curve import CoordinateSequence, LineString
from pysfcgal.geometry.geometry import Axis, Geometry
from pysfcgal.geometry.point import Point
from pysfcgal.geometry.surface import Polygon, PolyhedralSurface, Tin, Triangle
from pysfcgal.geometry.volume import Solid

__all__ = [
    "Axis",
    "BufferType",
    "CoordinateSequence",
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
]
