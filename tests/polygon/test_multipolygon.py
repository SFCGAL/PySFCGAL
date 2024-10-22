import icontract
import pytest

from pysfcgal.sfcgal import LineString, MultiPolygon, Polygon


@pytest.fixture
def multipolygon(ring_around_0, small_ring_23, small_ring_56):
    yield MultiPolygon([[ring_around_0], [small_ring_23], [small_ring_56]])


@pytest.fixture
def other_multipolygon(ring_around_0, small_ring_23, big_ring):
    yield MultiPolygon([[ring_around_0], [small_ring_23], [big_ring]])


@pytest.fixture
def multipolygon_unordered(ring_around_0, small_ring_23, small_ring_56):
    yield MultiPolygon([[small_ring_56], [ring_around_0], [small_ring_23]])


@pytest.fixture
def expected_polygons(ring_around_0, small_ring_23, small_ring_56):
    yield [Polygon(ring_around_0), Polygon(small_ring_23), Polygon(small_ring_56)]


def test_multilinestring_constructor(multipolygon):
    multipolygon_cloned = MultiPolygon(multipolygon.to_coordinates())
    assert multipolygon_cloned == multipolygon


def test_multipolygon_iteration(multipolygon, expected_polygons):
    for polygon, expected_polygon in zip(multipolygon, expected_polygons):
        assert polygon == expected_polygon


def test_multipolygon_indexing(multipolygon, expected_polygons):
    for idx in range(len(multipolygon)):
        assert multipolygon[idx] == expected_polygons[idx]
    assert multipolygon[-1] == expected_polygons[-1]
    assert multipolygon[1:3] == expected_polygons[1:3]


def test_multipolygon_equality(
    multipolygon, other_multipolygon, multipolygon_unordered
):
    assert multipolygon != other_multipolygon
    assert multipolygon != multipolygon_unordered  # the order is important


def test_multipolygon_to_coordinates(
    multipolygon, ring_around_0, small_ring_23, small_ring_56
):
    assert multipolygon.to_coordinates() == [
        [ring_around_0], [small_ring_23], [small_ring_56]
    ]
    cloned_multipolygon = MultiPolygon(multipolygon.to_coordinates())
    assert cloned_multipolygon == multipolygon
    other_multipolygon = MultiPolygon.from_coordinates(multipolygon.to_coordinates())
    assert other_multipolygon == multipolygon


def test_multipolygon_to_dict(multipolygon):
    multipolygon_data = multipolygon.to_dict()
    other_multipolygon = MultiPolygon.from_dict(multipolygon_data)
    assert other_multipolygon == multipolygon


def test_multipolygon_add_polygon(multipolygon, big_ring):
    new_polygon = Polygon(big_ring)
    assert len(multipolygon) == 3
    assert new_polygon not in multipolygon

    multipolygon.add_polygon(new_polygon)
    assert len(multipolygon) == 4
    assert new_polygon in multipolygon


def test_multipolygon_add_linestring_fails(multipolygon, c000, c100, c010):
    # try to add a linestring to a multipolygon
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        multipolygon.add_polygon(LineString([c000, c100, c010]))
