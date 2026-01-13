import pytest

from pysfcgal import sfcgal
from tests.utils import GEOMETRY_FACTORIES


@pytest.mark.parametrize(
    "geom_type,geom_factory",
    [(geom_type, factory) for geom_type, factory in GEOMETRY_FACTORIES.items()],
    ids=GEOMETRY_FACTORIES.keys()
)
def test_geom_to_dict(geom_type, geom_factory):
    geom = geom_factory(coord=0.)
    geom_data = geom.to_dict()
    geom_cls = sfcgal.geom_type_to_cls[sfcgal.geom_types[geom_type]]
    other_geom = geom_cls.from_dict(geom_data)
    assert other_geom == geom
