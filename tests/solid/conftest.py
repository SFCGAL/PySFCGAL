import pytest

from pysfcgal.sfcgal import MultiSolid, PolyhedralSurface, Solid
from tests.utils import create_cube_coordinates


@pytest.fixture
def points_ext_1():
    yield create_cube_coordinates(0., 10.)


@pytest.fixture
def points_ext_2():
    yield create_cube_coordinates(12., 25.)


@pytest.fixture
def points_int_1():
    yield create_cube_coordinates(2., 3.)


@pytest.fixture
def points_int_2():
    yield create_cube_coordinates(6., 8.)


@pytest.fixture
def expected_polyhedralsurfaces(points_ext_1, points_int_1, points_int_2):
    yield [
        PolyhedralSurface(points_ext_1),
        PolyhedralSurface(points_int_1),
        PolyhedralSurface(points_int_2),
    ]


@pytest.fixture
def composed_polyhedralsurface(points_ext_1, points_int_1, points_int_2):
    yield PolyhedralSurface(points_ext_1 + points_int_1 + points_int_2)


@pytest.fixture
def solid(points_ext_1, points_int_1, points_int_2):
    yield Solid([points_ext_1, points_int_1, points_int_2])


@pytest.fixture
def solid_without_holes(points_ext_1):
    yield Solid([points_ext_1])


@pytest.fixture
def solid_unordered(points_ext_1, points_int_1, points_int_2):
    yield Solid([points_ext_1, points_int_2, points_int_1])


@pytest.fixture
def multisolid(solid, solid_without_holes, solid_unordered):
    yield MultiSolid(
        [
            solid.to_coordinates(),
            solid_without_holes.to_coordinates(),
            solid_unordered.to_coordinates(),
        ]
    )


@pytest.fixture
def other_multisolid(solid):
    yield MultiSolid([solid.to_coordinates()])


@pytest.fixture
def multisolid_unordered(solid, solid_without_holes, solid_unordered):
    yield MultiSolid(
        [
            solid_without_holes.to_coordinates(),
            solid_unordered.to_coordinates(),
            solid.to_coordinates(),
        ]
    )


@pytest.fixture
def expected_solids(solid, solid_without_holes, solid_unordered):
    yield [solid, solid_without_holes, solid_unordered]
