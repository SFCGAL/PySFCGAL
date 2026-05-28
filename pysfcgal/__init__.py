from ._sfcgal import ffi, lib
from .geometry import (BufferType, CoordinateSequence, Geometry,
                       GeometryCollection, GeometrySequence, LineString,
                       MultiLineString, MultiPoint, MultiPolygon, MultiSolid,
                       Point, Polygon, PolyhedralSurface, Solid, Tin, Triangle)
from .vector import UNIT_X, UNIT_Y, UNIT_Z, Vector3D

__all__ = [
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
    "UNIT_X",
    "UNIT_Y",
    "UNIT_Z",
    "Vector3D",
    "sfcgal_version",
    "sfcgal_full_version",
]

# this must be called before anything else
lib.sfcgal_init()


def sfcgal_version():
    """Returns the version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_version()).decode("utf-8")
    return version


def sfcgal_full_version():
    """Returns the full version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_full_version()).decode("utf-8")
    return version
