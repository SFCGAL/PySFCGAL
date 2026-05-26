"""PySFCGAL geometry registry.

This module contains dictionaries that associates the different geometry types with the
corresponding classes in the PySFCGAL API.

"""

from pysfcgal.geometry.collection import (GeometryCollection, MultiLineString,
                                          MultiPoint, MultiPolygon, MultiSolid)
from pysfcgal.geometry.curve import LineString
from pysfcgal.geometry.point import Point
from pysfcgal.geometry.surface import Polygon, PolyhedralSurface, Tin, Triangle
from pysfcgal.geometry.volume import Solid

from .._sfcgal import lib

__all__ = ["geom_type_to_cls", "geom_types"]


# Mapping of geometry types to their respective classes
geom_type_to_cls = {
    lib.SFCGAL_TYPE_POINT: Point,
    lib.SFCGAL_TYPE_LINESTRING: LineString,
    lib.SFCGAL_TYPE_POLYGON: Polygon,
    lib.SFCGAL_TYPE_MULTIPOINT: MultiPoint,
    lib.SFCGAL_TYPE_MULTILINESTRING: MultiLineString,
    lib.SFCGAL_TYPE_MULTIPOLYGON: MultiPolygon,
    lib.SFCGAL_TYPE_GEOMETRYCOLLECTION: GeometryCollection,
    lib.SFCGAL_TYPE_TRIANGULATEDSURFACE: Tin,
    lib.SFCGAL_TYPE_TRIANGLE: Triangle,
    lib.SFCGAL_TYPE_POLYHEDRALSURFACE: PolyhedralSurface,
    lib.SFCGAL_TYPE_SOLID: Solid,
    lib.SFCGAL_TYPE_MULTISOLID: MultiSolid,
}

# Dictionary mapping geometry names to their corresponding type IDs
geom_types = {
    "Point": lib.SFCGAL_TYPE_POINT,
    "LineString": lib.SFCGAL_TYPE_LINESTRING,
    "Polygon": lib.SFCGAL_TYPE_POLYGON,
    "MultiPoint": lib.SFCGAL_TYPE_MULTIPOINT,
    "MultiLineString": lib.SFCGAL_TYPE_MULTILINESTRING,
    "MultiPolygon": lib.SFCGAL_TYPE_MULTIPOLYGON,
    "GeometryCollection": lib.SFCGAL_TYPE_GEOMETRYCOLLECTION,
    "TIN": lib.SFCGAL_TYPE_TRIANGULATEDSURFACE,
    "Triangle": lib.SFCGAL_TYPE_TRIANGLE,
    "PolyhedralSurface": lib.SFCGAL_TYPE_POLYHEDRALSURFACE,
    "Solid": lib.SFCGAL_TYPE_SOLID,
    "MultiSolid": lib.SFCGAL_TYPE_MULTISOLID,
}
