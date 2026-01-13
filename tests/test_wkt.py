import pytest

from pysfcgal import sfcgal


def point_factory(coord):
    return sfcgal.Point(coord, coord)


def linestring_factory(coord):
    return sfcgal.LineString(
        [
            [coord, coord],
            [coord, coord + 1]
        ]
    )


def polygon_factory(coord):
    return sfcgal.Polygon(
        [
            [coord, coord],
            [coord, coord + 1],
            [coord + 1, coord + 1],
            [coord + 1, coord]
        ]
    )


def geometry_collection_factory(coord):
    gc = sfcgal.GeometryCollection()
    gc.add_geometry(point_factory(coord))
    gc.add_geometry(linestring_factory(coord))
    gc.add_geometry(polygon_factory(coord))
    return gc


GEOMETRY_FACTORIES = {
    "Point": point_factory,
    "MultiPoint": lambda coord: sfcgal.MultiPoint([[coord, coord]]),
    "LineString": linestring_factory,
    "MultiLineString": lambda coord: sfcgal.MultiLineString(
        [[[coord, coord], [coord, coord + 1]]]
    ),
    "Polygon": polygon_factory,
    "MultiPolygon": lambda coord: sfcgal.MultiPolygon(
        [
            [
                [
                    [coord, coord],
                    [coord, coord + 1],
                    [coord + 1, coord + 1],
                    [coord + 1, coord]
                ]
            ]
        ]
    ),
    "GeometryCollection": geometry_collection_factory,
    "Triangle": lambda coord: sfcgal.Triangle(
        [
            [coord, coord],
            [coord, coord + 1],
            [coord + 1, coord]
        ]
    ),
    "TIN": lambda coord: sfcgal.Tin(
        [
            [
                [coord, coord],
                [coord, coord + 1],
                [coord + 1, coord]
            ]
        ]
    ),
    # "PolyhedralSurface": lambda coord: sfcgal.PolyhedralSurface(),
    # "Solid": lambda coord: sfcgal.Solid(),
    # "MultiSolid": lambda coord: sfcgal.MultiSolid(),
}


WKT_TOLERANCE_CASES = [
    (1/3, -1, True),
    (1/3, 0, False),
    (1/3, 1, False),
    (1/3, 8, False),
    (1, -1, True),
    (1, 0, True),
    (1, 1, True),
    (1, 8, True),
    (1.234, -1, True),
    (1.234, 0, False),
    (1.234, 1, False),
    (1.234, 8, True),
]


@pytest.mark.parametrize(
    "geom_factory",
    GEOMETRY_FACTORIES.values(),
    ids=GEOMETRY_FACTORIES.keys()
)
@pytest.mark.parametrize("coordinate,tolerance,expected_equality", WKT_TOLERANCE_CASES)
def test_geom_to_wkt(geom_factory, coordinate, tolerance, expected_equality):
    geom = geom_factory(coordinate)
    geom_wkt = geom.to_wkt(tolerance)
    other_geom = sfcgal.Geometry.from_wkt(geom_wkt)
    assert (other_geom == geom) == expected_equality
