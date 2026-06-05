import pytest

from tests.utils import GEOMETRY_FACTORIES


@pytest.mark.parametrize(
    "geom_type,geom_factory",
    [(geom_type, factory) for geom_type, factory in GEOMETRY_FACTORIES.items()],
    ids=GEOMETRY_FACTORIES.keys()
)
def test_lengths(geom_type, geom_factory):
    if geom_type in ("LineString", "MultiLineString", "GeometryCollection"):
        geom = geom_factory(coord=3.)
        assert geom.length == 1
    else:
        geom = geom_factory(coord=3.)
        assert geom.length == 0
