import pytest

from pysfcgal import sfcgal
from tests.utils import GEOMETRY_FACTORIES

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
