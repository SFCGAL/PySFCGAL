import itertools

from pysfcgal import sfcgal


def from_point_list_to_cube_coordinates(points):
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


def create_cube_coordinates(min_val=0, max_val=1):
    return from_point_list_to_cube_coordinates(
        [
            point_coord
            for point_coord
            in itertools.product((min_val, max_val), repeat=3)
        ]
    )


def point_factory(coord):
    return sfcgal.Point(coord, coord)


def multipoint_factory(coord):
    mp = sfcgal.MultiPoint()
    point = point_factory(coord)
    mp.add_point(point)
    return mp


def linestring_factory(coord):
    return sfcgal.LineString(
        [
            [coord, coord],
            [coord, coord + 1]
        ]
    )


def multilinestring_factory(coord):
    mline = sfcgal.MultiLineString()
    linestring = linestring_factory(coord)
    mline.add_linestring(linestring)
    return mline


def polygon_factory(coord):
    return sfcgal.Polygon(
        [
            [coord, coord],
            [coord, coord + 1],
            [coord + 1, coord + 1],
            [coord + 1, coord]
        ]
    )


def multipolygon_factory(coord):
    multipolygon = sfcgal.MultiPolygon()
    poly = polygon_factory(coord)
    multipolygon.add_polygon(poly)
    return multipolygon


def geometry_collection_factory(coord):
    gc = sfcgal.GeometryCollection()
    gc.add_geometry(point_factory(coord))
    gc.add_geometry(linestring_factory(coord))
    gc.add_geometry(polygon_factory(coord))
    return gc


def triangle_factory(coord):
    return sfcgal.Triangle(
        [
            [coord, coord],
            [coord, coord + 1],
            [coord + 1, coord]
        ]
    )


def tin_factory(coord):
    tin = sfcgal.Tin()
    triangle = triangle_factory(coord)
    tin.add_patch(triangle)
    return tin


def polyhedral_surface_factory(coord):
    coords = create_cube_coordinates(coord, coord + 1)
    return sfcgal.PolyhedralSurface(coords)


def solid_factory(coord):
    solid = sfcgal.Solid()
    phs = polyhedral_surface_factory(coord)
    solid.set_exterior_shell(phs)
    return solid


def multisolid_factory(coord):
    multisolid = sfcgal.MultiSolid()
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
