import pytest

from pysfcgal.sfcgal import Point


@pytest.fixture
def coords():
    x, y, z, m = 4, 5, 6, 7
    yield x, y, z, m


@pytest.fixture
def point_2d(coords):
    x, y = coords[:2]
    yield Point(x, y)


@pytest.fixture
def point_3d(coords):
    x, y, z = coords[:3]
    yield Point(x, y, z)


@pytest.fixture
def point_4d(coords):
    yield Point(*coords)


@pytest.fixture
def point_3dm(coords):
    x, y, _, m = coords
    yield Point(x, y, m=m)


@pytest.mark.parametrize(
    "x,y,z,m",
    [
        (1, None, None, None),
        (None, 2, None, None),
        (None, None, 3, None),
        (None, None, None, 4),
        (None, None, 3, 4),
    ]
)
def test_point_wrong_param(x, y, z, m):
    with pytest.raises(ValueError):
        _ = Point(x, y, z, m)


@pytest.mark.parametrize(
    "point_fixture, coordinates",
    [
        ("point_3d", (4, 5, 6)),
        ("point_2d", (4, 5)),
        ("point_4d", (4, 5, 6, 7)),
        ("point_3dm", (4, 5, None, 7)),
    ]
)
def test_point_to_coordinates(point_fixture, coordinates, request):
    point = request.getfixturevalue(point_fixture)
    assert point.x == coordinates[0]
    assert point.y == coordinates[1]
    if point_fixture in ("point_3d", "point_4d"):
        assert point.has_z
        assert point.z == coordinates[2]
    if point_fixture in ("point_3dm", "point_4d"):
        assert point.has_m
        assert point.m == coordinates[3]
    assert point.to_coordinates() == coordinates
    other_point = Point.from_coordinates(point.to_coordinates())
    assert point == other_point
    other_point = Point(*point.to_coordinates())
    assert other_point == point


def test_point_to_dict(point_3d):
    point_data = point_3d.to_dict()
    other_point = Point.from_dict(point_data)
    assert other_point == point_3d


def test_point_equivalence(point_2d, point_3d, point_3dm):
    assert not point_2d == point_3d
    assert not point_3dm == point_3d


def test_point_drop_z_m(point_3d, point_3dm, point_4d):
    assert point_3d.has_z
    assert not point_3d.has_m
    new_pt = point_3d.drop_z()
    assert point_3d.has_z
    assert not new_pt.has_z
    point_3d.drop_z(True)
    assert not point_3d.has_z

    assert not point_3dm.has_z
    assert point_3dm.has_m
    new_pt = point_3dm.drop_m()
    assert point_3dm.has_m
    assert not new_pt.has_m
    point_3dm.drop_m(True)
    assert not point_3dm.has_m

    assert point_4d.has_z
    assert point_4d.has_m
    new_pt = point_4d.drop_z()
    assert not new_pt.has_z
    assert new_pt.has_m
    assert point_4d.has_z
    assert point_4d.has_m
    point_4d.drop_z(True)
    assert not point_4d.has_z
    assert point_4d.has_m
    new_pt = point_4d.drop_m()
    assert not new_pt.has_z
    assert not new_pt.has_m
    assert not point_4d.has_z
    assert point_4d.has_m
    point_4d.drop_m(True)
    assert not point_4d.has_z
    assert not point_4d.has_m


def test_point_force_z_m(coords, point_2d, point_3d, point_3dm, point_4d):
    x, y, z, m = coords

    # point 2d
    assert not point_2d.has_z
    assert not point_2d.has_m
    new_pt = point_2d.force_z()
    assert new_pt.has_z
    assert not new_pt.has_m
    assert not point_2d.has_z
    assert not point_2d.has_m
    assert new_pt == Point(x, y, 0)

    new_pt = point_2d.force_z(1.2)
    assert new_pt.has_z
    assert not new_pt.has_m
    assert new_pt == Point(x, y, 1.2)

    point_2d.force_z(inplace=True)
    assert point_2d.has_z
    assert not point_2d.has_m
    assert point_2d == Point(x, y, 0)

    new_pt = point_2d.force_m(4.2)
    assert point_2d.has_z
    assert not point_2d.has_m
    assert new_pt.has_m
    assert new_pt == Point(x, y, 0, 4.2)

    # point 3d
    assert point_3d.has_z
    assert not point_3d.has_m
    new_pt = point_3d.force_z()  # no effect
    assert new_pt == point_3d
    new_pt = point_3d.force_z(4.5)  # no effect
    assert new_pt == point_3d

    new_pt = point_3d.force_m(1.2)  # no effect
    assert new_pt == Point(x, y, z, 1.2)

    # point 3dm
    assert not point_3dm.has_z
    assert point_3dm.has_m
    new_pt = point_3dm.force_z(-2.1)
    assert new_pt.has_z
    assert new_pt.has_m
    assert not point_3dm.has_z
    assert point_3dm.has_m
    assert new_pt == Point(x, y, -2.1, m)

    point_3dm.force_z(4.4, True)
    assert point_3dm.has_z
    assert point_3dm.has_m
    assert point_3dm == Point(x, y, 4.4, m=m)

    point_3dm.force_z(-5.6, True)  # no effect
    assert point_3dm == Point(x, y, 4.4, m=m)

    # point 4d
    assert point_4d.has_z
    assert point_4d.has_m
    new_pt = point_4d.force_z()  # no effect
    assert new_pt == point_4d
    new_pt = point_4d.force_z(4.5)  # no effect
    assert new_pt == point_4d
    new_pt = point_4d.force_m()  # no effect
    assert new_pt == point_4d
    new_pt = point_4d.force_m(2.04)  # no effect
    assert new_pt == point_4d
