"""This module introduces a range of geometry factories dedicated to unit tests.

Every factory intends to generate a simple geometry starting from a single coordinate
value.

"""

import itertools

from pysfcgal import (GeometryCollection, LineString, MultiLineString,
                      MultiPoint, MultiPolygon, MultiSolid, Point, Polygon,
                      PolyhedralSurface, Solid, Tin, Triangle)


def from_point_list_to_cube_coordinates(
    points: list[tuple[float]]
) -> list[list[tuple[float]]]:
    """Reorder a list of point coordinates so as to have cube coordinates.

    The output coordinates are ordered in such a way the resulting cube will be a valid
    PySFCGAL geometry (PolyhedralSurface).

    Parameters
    ----------
    points : list[tuple[float]]
        The coordinates of 8 points considered as the cube vertices.

    Returns
    -------
    list[list[tuple[float]]]
        A valid PolyhedralSurface set of coordinates.

    """
    return [
        [
            [points[0], points[2], points[6], points[4], points[0]]
        ],  # bottom face
        [
            [points[1], points[5], points[7], points[3], points[1]]
        ],  # up face
        [
            [points[0], points[1], points[3], points[2], points[0]]
        ],  # left face
        [
            [points[2], points[3], points[7], points[6], points[2]]
        ],  # front face
        [
            [points[6], points[7], points[5], points[4], points[6]]
        ],  # right face
        [
            [points[4], points[5], points[1], points[0], points[4]]
        ],  # back face
    ]


def create_cube_coordinates(
    min_val: float = 0, max_val: float = 1
) -> list[list[tuple[float]]]:
    """Generate a set of coordinates as a basis for a cube.

    The input values denote an implicit bounding box, where all vertices are defined.
    One basically has a first point at the (min_val, min_val, min_val) coordinates and
    an other point at (max_val, max_val, max_val) coordinates.

    The output cube will be valid PolyhedralSurface, regarding the coordinates ordering.

    Parameters
    ----------
    min_val : float
        The smallest coordinate.
    max_val : float
        The biggest coordinate.

    Returns
    -------
    list[list[tuple[float]]]
        A valid PolyhedralSurface set of coordinates.

    """
    return from_point_list_to_cube_coordinates(
        [
            point_coord
            for point_coord
            in itertools.product((min_val, max_val), repeat=3)
        ]
    )


def point_factory(coord: float) -> Point:
    """Return a simple 3D Point with X, Y and Z coordinates.

    X, Y and Z are equal.

    Attributes
    ----------
    coord: float
        Unique value for every coordinate.

    Returns
    -------
    sfcgal.Point
        A simple PointZ.
    """
    return Point(coord, coord, coord)


def multipoint_factory(coord: float) -> MultiPoint:
    """Return a simple 3D MultiPoint with X, Y and Z coordinates.

    X, Y and Z are equal, and the MultiPoint contains only a single point.

    Attributes
    ----------
    coord: float
        Unique value for every coordinate.

    Returns
    -------
    MultiPoint
        A simple MultiPointZ.
    """
    mp = MultiPoint()
    point = point_factory(coord)
    mp.add_point(point)
    return mp


def linestring_factory(coord: float) -> LineString:
    """Return a simple vertical 3D LineString starting from a unique coordinate value.

    The X, Y and Z coordinates are equal, the LineStringZ is drawn considering Z and Z+1
    (X and Y does not evolve).

    Attributes
    ----------
    coord: float
        Base value for the LineStringZ coordinates.

    Returns
    -------
    LineString
        A simple vertical LineStringZ.

    """
    return LineString(
        [
            [coord, coord, coord],
            [coord, coord + 1, coord + 1]
        ]
    )


def multilinestring_factory(coord: float) -> MultiLineString:
    """Return a simple 3D MultiLineString starting from a unique coordinate value.

    The MultiLineString contains only a single LineStringZ, in which the X, Y and Z
    coordinates are equal, the LineStringZ is drawn considering Z and Z+1 (X and Y does
    not evolve).

    Attributes
    ----------
    coord: float
        Base value for the LineStringZ coordinates.

    Returns
    -------
    MultiLineString
        A simple MultiLineStringZ composed of a single vertical LineStringZ.

    """
    mline = MultiLineString()
    linestring = linestring_factory(coord)
    mline.add_linestring(linestring)
    return mline


def polygon_factory(coord: float) -> Polygon:
    """Return a simple 3D Polygon starting from a unique coordinate value.

    The PolygonZ is defined with four vertices; the vertice coordinates are such that X
    and Y vary around the input coordinate value (whilst Z is fixed).

    Attributes
    ----------
    coord: float
        Base value for the PolygonZ coordinates.

    Returns
    -------
    Polygon
        A simple PolygonZ.

    """
    return Polygon(
        [
            [coord, coord, coord],
            [coord, coord + 1, coord],
            [coord + 1, coord + 1, coord],
            [coord + 1, coord, coord]
        ]
    )


def multipolygon_factory(coord: float) -> MultiPolygon:
    """Return a simple 3D MultiPolygon starting from a unique coordinate value.

    The MultiPolygon contains only a single PolygonZ, designed from the polygon factory.

    Attributes
    ----------
    coord: float
        Base value for the MultiPolygonZ coordinates.

    Returns
    -------
    MultiPolygon
        A simple MultiPolygonZ.

    """
    multipolygon = MultiPolygon()
    poly = polygon_factory(coord)
    multipolygon.add_polygon(poly)
    return multipolygon


def geometry_collection_factory(coord: float) -> GeometryCollection:
    """Return a simple 3D GeometryCollection starting from a unique coordinate value.

    The geometries that compose the collection are drawn with their respective factory.

    Attributes
    ----------
    coord: float
        Base value for the coordinates of the geometries contained into the collection.

    Returns
    -------
    GeometryCollection
        A GeometryCollection containing a PointZ, a LineStringZ and a PolygonZ.

    """
    gc = GeometryCollection()
    gc.add_geometry(point_factory(coord))
    gc.add_geometry(linestring_factory(coord))
    gc.add_geometry(polygon_factory(coord))
    return gc


def triangle_factory(coord: float) -> Triangle:
    """Return a simple 3D Triangle starting from a unique coordinate value.

    The triangle vertice coordinates are such that X and Y vary around the input
    coordinate value (whilst Z is fixed).

    Attributes
    ----------
    coord: float
        Base value for the TriangleZ coordinates.

    Returns
    -------
    Triangle
        A simple TriangleZ.

    """
    return Triangle(
        [
            [coord, coord, coord],
            [coord, coord + 1, coord],
            [coord + 1, coord, coord]
        ]
    )


def tin_factory(coord: float) -> Tin:
    """Return a simple 3D TIN starting from a unique coordinate value.

    The TIN contains only a single TriangleZ, designed from the triangle factory.

    Attributes
    ----------
    coord: float
        Base value for the TIN Z coordinates.

    Returns
    -------
    Tin
        A simple TIN Z with a single triangle.

    """
    tin = Tin()
    triangle = triangle_factory(coord)
    tin.add_patch(triangle)
    return tin


def polyhedral_surface_factory(coord: float) -> PolyhedralSurface:
    """Return a simple 3D PolyhedralSurface starting from a unique coordinate value.

    The PolyhedralSurface is defined as a cube, its vertice coordinates vary around the
    input value.

    Attributes
    ----------
    coord: float
        Base value for the cube coordinates.

    Returns
    -------
    PolyhedralSurface
        A simple cubic PolyhedralSurface.

    """
    coords = create_cube_coordinates(coord, coord + 1)
    return PolyhedralSurface(coords)


def solid_factory(coord: float) -> Solid:
    """Return a simple Solid starting from a unique coordinate value.

    The Solid only has an exterior shell, which is a cube designed from the polyhedral
    surface factory.

    Attributes
    ----------
    coord: float
        Base value for the Solid coordinates.

    Returns
    -------
    Solid
        A simple Solid with only an exterior shell.

    """
    solid = Solid()
    phs = polyhedral_surface_factory(coord)
    solid.set_exterior_shell(phs)
    return solid


def multisolid_factory(coord: float) -> MultiSolid:
    """Return a simple MultiSolid starting from a unique coordinate value.

    The MultiSolid contains only a single Solid, designed from the solid factory.

    Attributes
    ----------
    coord: float
        Base value for the MultiSolid coordinates.

    Returns
    -------
    MultiSolid
        A simple MultiSolid that contains a single Solid.

    """
    multisolid = MultiSolid()
    solid = solid_factory(coord)
    multisolid.add_solid(solid)
    return multisolid


GEOMETRY_FACTORIES = {
    "Point": point_factory,
    "MultiPoint": multipoint_factory,
    "LineString": linestring_factory,
    "MultiLineString": multilinestring_factory,
    "Polygon": polygon_factory,
    "MultiPolygon": multipolygon_factory,
    "GeometryCollection": geometry_collection_factory,
    "Triangle": triangle_factory,
    "TIN": tin_factory,
    "PolyhedralSurface": polyhedral_surface_factory,
    "Solid": solid_factory,
    "MultiSolid": multisolid_factory,
}
