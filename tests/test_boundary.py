import pytest

from pysfcgal import Geometry
from tests.utils import GEOMETRY_FACTORIES

WKT_EXPECTED_BOUNDARIES = {
    "Point": "GEOMETRYCOLLECTION EMPTY",
    "MultiPoint": "GEOMETRYCOLLECTION EMPTY",
    "LineString": "MULTIPOINT Z ((1 1 1),(1 1 2))",
    "MultiLineString": "MULTIPOINT Z ((1 1 2),(1 1 1))",
    "Polygon": "LINESTRING Z (1 1 1,1 2 1,2 2 1,2 1 1,1 1 1)",
    "MultiPolygon": "MULTILINESTRING Z ((1 1 1,1 2 1),(1 2 1,2 2 1),(2 2 1,2 1 1),(2 1 1,1 1 1))",  # noqa: E501
    "GeometryCollection": None,
    "Triangle": "LINESTRING Z (1 1 1,1 2 1,2 1 1,1 1 1)",
    "TIN": "MULTILINESTRING Z ((1 1 1,1 2 1),(1 2 1,2 1 1),(2 1 1,1 1 1))",
    "PolyhedralSurface": "GEOMETRYCOLLECTION EMPTY",
    "Solid": None,
    "MultiSolid": None,
}


@pytest.mark.parametrize(
    "geom_factory, wkt_expected_boundary",
    [
        (GEOMETRY_FACTORIES[name], WKT_EXPECTED_BOUNDARIES[name])
        for name in GEOMETRY_FACTORIES
    ],
    ids=GEOMETRY_FACTORIES.keys(),
)
def test_boundary(geom_factory, wkt_expected_boundary):
    geom = geom_factory(1)
    boundary = geom.boundary()
    expected_boundary = Geometry.from_wkt(wkt_expected_boundary)
    assert boundary == expected_boundary
    # not xor, ensure both predicates have the same value
    assert not (wkt_expected_boundary is None) ^ (boundary is None)
