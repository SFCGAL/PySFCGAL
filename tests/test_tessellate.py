from pysfcgal import (Geometry, GeometryCollection, LineString,
                      MultiLineString, Point, Polygon)


def test_simple_polygon():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tessellation = poly.tessellate()
    expected_wkt = "TIN (((0 1,1 0,1 1,0 1)),((0 1,0 0,1 0,0 1)))"
    expected_geom = Geometry.from_wkt(expected_wkt)
    assert tessellation.covers(expected_geom)


def test_polygon_with_an_hole():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [
                [(.2, .2), (.2, .8), (.8, .8), (.8, .2)]])
    tessellation = poly.tessellate()
    expected_wkt = (
        "TIN (((0.8 0.2,0.2 0.2,1.0 0.0,0.8 0.2)),"
        "((0.2 0.2,0.0 0.0,1.0 0.0,0.2 0.2)),"
        "((1.0 1.0,0.8 0.8,0.8 0.2,1.0 1.0)),"
        "((0.0 1.0,0.0 0.0,0.2 0.2,0.0 1.0)),"
        "((0.0 1.0,0.2 0.8,1.0 1.0,0.0 1.0)),"
        "((0.0 1.0,0.2 0.2,0.2 0.8,0.0 1.0)),"
        "((0.2 0.8,0.8 0.8,1.0 1.0,0.2 0.8)),"
        "((1.0 1.0,0.8 0.2,1.0 0.0,1.0 1.0)))")
    expected_geom = Geometry.from_wkt(expected_wkt)
    assert tessellation.covers(expected_geom)


def test_polygon_with_breaklines():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    lines = [LineString([(.2, .6), (.8, .6)]),
             LineString([(.2, .4), (.8, .4)])]
    geom = GeometryCollection()
    geom.add_geometry(poly)
    for line in lines:
        geom.add_geometry(line)
    tessellation = geom.tessellate()
    geom2 = GeometryCollection.from_wkt("""GEOMETRYCOLLECTION (
    TRIANGLE ((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),
    TRIANGLE ((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),
    TRIANGLE ((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),
    TRIANGLE ((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),
    TRIANGLE ((0.2 0.6,1.0 1.0,0.0 1.0,0.2 0.6)),
    TRIANGLE ((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),
    TRIANGLE ((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),
    TRIANGLE ((0.8 0.6,1.0 1.0,0.2 0.6,0.8 0.6)),
    TRIANGLE ((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),
    TRIANGLE ((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)))""")
    assert tessellation.covers(geom2)


def test_polygon_with_breaklines_point():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    multiline = MultiLineString([[(.2, .6), (.8, .6)], [(.2, .4), (.8, .4)]])
    point = Point(.9, .9)
    geom = GeometryCollection()
    geom.add_geometry(poly)
    geom.add_geometry(multiline)
    geom.add_geometry(point)
    tessellation = geom.tessellate()
    geom2 = GeometryCollection.from_wkt("""GEOMETRYCOLLECTION (
    TRIANGLE ((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),
    TRIANGLE ((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),
    TRIANGLE ((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),
    TRIANGLE ((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),
    TRIANGLE ((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),
    TRIANGLE ((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),
    TRIANGLE ((0.2 0.6,0.9 0.9,0.0 1.0,0.2 0.6)),
    TRIANGLE ((0.8 0.6,0.9 0.9,0.2 0.6,0.8 0.6)),
    TRIANGLE ((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)),
    TRIANGLE ((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),
    TRIANGLE ((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),
    TRIANGLE ((0.8 0.6,1.0 1.0,0.9 0.9,0.8 0.6)))""")
    assert tessellation.covers(geom2)


def test_polygon_with_points():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    point = Point(.9, .9)
    geom = GeometryCollection()
    geom.add_geometry(poly)
    geom.add_geometry(point)
    tessellation = geom.tessellate()
    geom2 = GeometryCollection.from_wkt("""GEOMETRYCOLLECTION (
    TRIANGLE ((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),
    TRIANGLE ((0.0 0.0,1.0 0.0,0.9 0.9,0.0 0.0)),
    TRIANGLE ((0.0 0.0,0.9 0.9,0.0 1.0,0.0 0.0)),
    TRIANGLE ((1.0 0.0,1.0 1.0,0.9 0.9,1.0 0.0)))""")
    assert tessellation.covers(geom2)


def test_polygon_with_quasi_collinear_points():
    poly = Polygon([(-4.165589, -29.100525),
                    (8.623957000000001, -28.461553),
                    (21.413503, -27.822581),
                    (10.706928, -13.90117),
                    (0.000353, 0.020242),
                    (-2.082618, -14.540141),
                    (-4.165589, -29.100525)])
    tessellation = poly.tessellate()
    expected_wkt = (
        "TIN (((-2.082618 -14.540141,8.623957 -28.461553,10.706928 -13.901170,"
        "-2.082618 -14.540141)),"
        "((10.706928 -13.901170,8.623957 -28.461553,21.413503 -27.822581,"
        "10.706928 -13.901170)),"
        "((-2.082618 -14.540141,10.706928 -13.901170,0.000353 0.020242,"
        "-2.082618 -14.540141)),"
        "((-4.165589 -29.100525,8.623957 -28.461553,-2.082618 -14.540141,"
        "-4.165589 -29.100525)))"
    )
    expected_geom = Geometry.from_wkt(expected_wkt)
    assert tessellation.covers(expected_geom)


def test_polygon_with_hole_and_break_lines():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [
                [(.2, .2), (.2, .8), (.8, .8), (.8, .2)]])
    lines = [LineString([(.1, .1), (.9, .1)]),
             LineString([(.9, .1), (.9, .9)]),
             LineString([(.9, .9), (.1, .9)]),
             LineString([(.1, .9), (.1, .1)])]
    geom = GeometryCollection()
    geom.add_geometry(poly)
    for line in lines:
        geom.add_geometry(line)
    tessellation = geom.tessellate()
    geom2 = GeometryCollection.from_wkt("""GEOMETRYCOLLECTION (
    TRIANGLE ((0.0 0.0,1.0 0.0,0.1 0.1,0.0 0.0)),
    TRIANGLE ((0.0 0.0,0.1 0.1,0.0 1.0,0.0 0.0)),
    TRIANGLE ((0.1 0.9,1.0 1.0,0.0 1.0,0.1 0.9)),
    TRIANGLE ((0.1 0.1,0.1 0.9,0.0 1.0,0.1 0.1)),
    TRIANGLE ((0.1 0.1,0.9 0.1,0.2 0.2,0.1 0.1)),
    TRIANGLE ((0.1 0.1,1.0 0.0,0.9 0.1,0.1 0.1)),
    TRIANGLE ((0.2 0.8,0.9 0.9,0.1 0.9,0.2 0.8)),
    TRIANGLE ((0.1 0.1,0.2 0.2,0.1 0.9,0.1 0.1)),
    TRIANGLE ((0.2 0.2,0.2 0.8,0.1 0.9,0.2 0.2)),
    TRIANGLE ((0.9 0.9,1.0 1.0,0.1 0.9,0.9 0.9)),
    TRIANGLE ((0.2 0.2,0.9 0.1,0.8 0.2,0.2 0.2)),
    TRIANGLE ((0.8 0.8,0.9 0.9,0.2 0.8,0.8 0.8)),
    TRIANGLE ((0.9 0.1,0.9 0.9,0.8 0.2,0.9 0.1)),
    TRIANGLE ((0.8 0.2,0.9 0.9,0.8 0.8,0.8 0.2)),
    TRIANGLE ((0.9 0.1,1.0 1.0,0.9 0.9,0.9 0.1)),
    TRIANGLE ((1.0 0.0,1.0 1.0,0.9 0.1,1.0 0.0)))""")
    assert tessellation.covers(geom2)
