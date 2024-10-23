import itertools

import pytest

from pysfcgal.sfcgal import MultiSolid, PolyhedralSurface, Solid


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
