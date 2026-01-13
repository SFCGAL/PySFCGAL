import icontract
import pytest

from pysfcgal.sfcgal import LineString, MultiPolygon, Polygon


@pytest.fixture
def multipolygon(ring_around_0_ccw, small_ring_23_ccw, small_ring_56_ccw):
    yield MultiPolygon([[ring_around_0_ccw], [small_ring_23_ccw], [small_ring_56_ccw]])


@pytest.fixture
def other_multipolygon(ring_around_0_ccw, small_ring_23_ccw, small_ring_67_ccw):
    yield MultiPolygon([[ring_around_0_ccw], [small_ring_23_ccw], [small_ring_67_ccw]])


@pytest.fixture
def multipolygon_unordered(ring_around_0_ccw, small_ring_23_ccw, small_ring_56_ccw):
    yield MultiPolygon([[small_ring_56_ccw], [ring_around_0_ccw], [small_ring_23_ccw]])


@pytest.fixture
def vertical_multipolygon(vertical_ring):
    yield MultiPolygon([[vertical_ring]])


@pytest.fixture
def expected_polygons(ring_around_0_ccw, small_ring_23_ccw, small_ring_56_ccw):
    yield [
        Polygon(ring_around_0_ccw),
        Polygon(small_ring_23_ccw),
        Polygon(small_ring_56_ccw)
    ]


def test_multipolygon_valid(multipolygon, other_multipolygon):
    assert multipolygon.is_valid()
    assert other_multipolygon.is_valid()


def test_multipolygon_constructor(multipolygon):
    multipolygon_cloned = MultiPolygon(multipolygon.to_coordinates())
    assert multipolygon_cloned.is_valid()
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
    multipolygon, ring_around_0_ccw, small_ring_23_ccw, small_ring_56_ccw
):
    assert multipolygon.to_coordinates() == [
        [ring_around_0_ccw], [small_ring_23_ccw], [small_ring_56_ccw]
    ]
    cloned_multipolygon = MultiPolygon(multipolygon.to_coordinates())
    assert cloned_multipolygon == multipolygon
    other_multipolygon = MultiPolygon.from_coordinates(multipolygon.to_coordinates())
    assert other_multipolygon == multipolygon


def test_multipolygon_to_dict(multipolygon):
    multipolygon_data = multipolygon.to_dict()
    other_multipolygon = MultiPolygon.from_dict(multipolygon_data)
    assert other_multipolygon == multipolygon


def test_multipolygon_add_polygon(multipolygon, big_ring_ccw):
    new_polygon = Polygon(big_ring_ccw)
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


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_centroid_vertical(
    vertical_multipolygon: MultiPolygon, compute_2d_area: bool
) -> None:
    assert (
        vertical_multipolygon.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area
