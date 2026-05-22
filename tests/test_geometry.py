import pytest

from pysfcgal.geometry.registry import geom_type_to_cls, geom_types
from tests.utils import GEOMETRY_FACTORIES


@pytest.mark.parametrize(
    "geom_type, geom_cls",
    [
        (geom_type, geom_type_to_cls[sfcgal_geom])
        for geom_type, sfcgal_geom in geom_types.items()
    ]
)
def test_geometry_empty(geom_type, geom_cls):
    """For every geometry class in PySFCGAL, building an instance with a default
    pararametrization should produce an empty geometry.

    """
    geom = geom_cls()
    assert geom.to_wkt() == f"{geom_type} EMPTY".upper()


@pytest.mark.parametrize(
    "geom_factory",
    GEOMETRY_FACTORIES.values(),
    ids=GEOMETRY_FACTORIES.keys()
)
def test_is_valid(geom_factory) -> None:
    """A geometry may be valid by itself, without setting the validity flag.

    By default, the validity flag is unset.
    """
    geom = geom_factory(1.)
    assert not geom.validity_flag
    assert geom.is_valid()  # updates the validity flag on the same hand
    assert geom.validity_flag
    # Testing the validity flag modification
    geom.validity_flag = False
    assert not geom.validity_flag
