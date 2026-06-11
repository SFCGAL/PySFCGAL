import pytest

from pysfcgal.geometry import Geometry, Point
from pysfcgal.vector import Vector3D

MIRROR_TESTS = [
    (
        "POINT Z (2 0 1)",
        "POINT Z (-2 0 1)",
        "POINT Z (2 0 -1)",
        "POINT Z (2 0 1)",
    ),
    (
        "LINESTRING Z (0 0 1,3 0 1,3 3 1)",
        "LINESTRING Z (0 0 1,-3 0 1,-3 3 1)",
        "LINESTRING Z (0 0 -1,3 0 -1,3 3 -1)",
        "LINESTRING Z (0 0 1,3 0 1,3 -3 1)",
    ),
    (
        "POLYGON Z ((0 0 2,2 0 2,2 2 2,0 2 2,0 0 2))",
        "POLYGON Z ((0 0 2,-2 0 2,-2 2 2,0 2 2,0 0 2))",
        "POLYGON Z ((0 0 -2,2 0 -2,2 2 -2,0 2 -2,0 0 -2))",
        "POLYGON Z ((0 0 2,2 0 2,2 -2 2,0 -2 2,0 0 2))",
    ),
]


@pytest.mark.parametrize(
    "input_wkt, expected_yz, expected_xy, expected_xz", MIRROR_TESTS)
def test_mirror(input_wkt, expected_yz, expected_xy, expected_xz):
    geom = Geometry.from_wkt(input_wkt)
    assert geom.is_valid()

    # mirror yz
    plane_point = Point(0.0, 0.0, 0.0)
    plane_normal = Vector3D(1.0, 0.0, 0.0)
    mirror_geom_yz = geom.mirror(plane_point, plane_normal)
    assert mirror_geom_yz.is_valid()

    expected_geom_yz = Geometry.from_wkt(expected_yz)
    assert mirror_geom_yz.covers_3d(expected_geom_yz)

    same_mirror_geom_yz = geom.mirror_yz()
    assert same_mirror_geom_yz == mirror_geom_yz

    # mirror xy
    mirror_xy = geom.mirror_xy()
    expected_geom_xy = Geometry.from_wkt(expected_xy)
    assert mirror_xy.covers_3d(expected_geom_xy)

    # mirror xz
    mirror_xz = geom.mirror_xz()
    expected_geom_xz = Geometry.from_wkt(expected_xz)
    assert mirror_xz.covers_3d(expected_geom_xz)
