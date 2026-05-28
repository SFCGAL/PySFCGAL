import icontract
import pytest

from pysfcgal import LineString, MultiLineString, Point


@pytest.fixture
def multilinestring(c000, c100, c010, c001):
    yield MultiLineString([[c000, c100], [c000, c010], [c000, c001]])


@pytest.fixture
def other_multilinestring(c000, c100, c010):
    yield MultiLineString([[c000, c100], [c000, c010]])


@pytest.fixture
def multilinestring_unordered(c000, c100, c010, c001):
    yield MultiLineString([[c000, c001], [c000, c100], [c000, c010]])


@pytest.fixture
def expected_linestrings(lineX, lineY, lineZ):
    yield [lineX, lineY, lineZ]


@pytest.fixture
def vertical_multilinestring(c000, c100, c001):
    yield MultiLineString([[c000, c100, c001]])


@pytest.fixture
def closed_vertical_multilinestring(vertical_multilinestring):
    vertical_multilinestring_coords = vertical_multilinestring.to_coordinates()
    yield MultiLineString(
        [
            coords + [coords[0]]
            for coords in vertical_multilinestring_coords
        ]
    )


def test_multilinestring_constructor(multilinestring):
    multilinestring_cloned = MultiLineString(multilinestring.to_coordinates())
    assert multilinestring_cloned == multilinestring


def test_multilinestring_iteration(multilinestring, expected_linestrings):
    for linestring, expected_linestring in zip(multilinestring, expected_linestrings):
        assert linestring == expected_linestring


def test_multilinestring_indexing(multilinestring, expected_linestrings):
    for idx in range(len(multilinestring)):
        assert multilinestring[idx] == expected_linestrings[idx]
    assert multilinestring[-1] == expected_linestrings[-1]
    assert multilinestring[1:3] == expected_linestrings[1:3]


def test_multilinestring_equality(
    multilinestring, other_multilinestring, multilinestring_unordered
):
    assert multilinestring != other_multilinestring
    assert multilinestring != multilinestring_unordered  # the order is important


def test_multilinestring_to_coordinates(multilinestring, c000, c100, c010, c001):
    assert multilinestring.to_coordinates() == [
        [c000, c100], [c000, c010], [c000, c001]
    ]
    cloned_multilinestring = MultiLineString(multilinestring.to_coordinates())
    assert cloned_multilinestring == multilinestring
    other_multilinestring = MultiLineString.from_coordinates(
        multilinestring.to_coordinates()
    )
    assert other_multilinestring == multilinestring


def test_multilinestring_add_linestring(multilinestring, c100, c010):
    new_line = LineString([c100, c010])
    assert len(multilinestring) == 3
    assert new_line not in multilinestring

    multilinestring.add_linestring(new_line)
    assert len(multilinestring) == 4
    assert new_line in multilinestring


def test_multilinestring_add_point_fails(multilinestring, c100):
    # try to add a point to a multilinestring
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        multilinestring.add_linestring(Point(*c100))


def test_multilinestring_set_linestring_n(multilinestring, c100, c010):
    new_line = LineString([c100, c010])
    assert len(multilinestring) == 3
    assert new_line not in multilinestring

    multilinestring.set_linestring_n(new_line, 1)
    assert len(multilinestring) == 3
    assert new_line in multilinestring


def test_centroid(multilinestring: MultiLineString) -> None:
    assert multilinestring.centroid() == multilinestring.centroid(True)


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_vertical_centroid(
    closed_vertical_multilinestring: MultiLineString, compute_2d_area: bool
) -> None:
    assert (
        closed_vertical_multilinestring.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area
