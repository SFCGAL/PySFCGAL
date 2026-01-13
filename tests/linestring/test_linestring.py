import pytest

from pysfcgal.sfcgal import LineString


@pytest.fixture
def long_line(c000, c100, c010, c001):
    yield LineString([c000, c100, c010, c001])


@pytest.fixture
def vertical_line(c000, c100, c001):
    yield LineString([c000, c100, c001])


@pytest.fixture
def closed_vertical_line(vertical_line):
    vertical_line_coords = vertical_line.to_coordinates()
    yield LineString(vertical_line_coords + [vertical_line_coords[0]])


@pytest.mark.parametrize(
    "linestring,expected_length", [("line", 4), ("long_line", 9)],
)
def test_linestring_len(linestring, expected_length):
    assert len(linestring) == expected_length


def test_linestring_to_coordinates(long_line, c000, c100, c010, c001):
    coords = long_line.to_coordinates()
    assert len(coords) == 4
    assert coords[0] == c000
    assert coords[-1] == c001
    assert coords[0:2] == [c000, c100]
    cloned_linestring = LineString(coords)
    assert cloned_linestring == long_line
    other_linestring = LineString.from_coordinates(coords)
    assert other_linestring == long_line


def test_linestring_coordinate_sequence(long_line, c000, c100, c010, c001):
    for coord_in_sequence, expected_coord in zip(
        long_line.coords, [c000, c100, c010, c001]
    ):
        assert coord_in_sequence == expected_coord
    for coord_in_sequence, coordinate in zip(
        long_line.coords, long_line.to_coordinates()
    ):
        assert coord_in_sequence == coordinate


def test_linestring_to_dict(long_line):
    linestring_data = long_line.to_dict()
    other_line = LineString.from_dict(linestring_data)
    assert other_line == long_line


def test_linestring_eq(long_line, lineX, lineY):
    assert long_line != lineX
    assert lineX != lineY
    assert long_line[:2] == lineX[:]


def test_linestring_getter(long_line):
    # Indexing with a wrong type
    with pytest.raises(TypeError):
        _ = long_line["cant-index-with-a-string"]
    # Positive indexing
    for idx, p in enumerate(long_line):
        assert long_line[idx] == p
    with pytest.raises(IndexError):
        _ = long_line[99]
    # Negative indexing
    for idx, p in enumerate(reversed(long_line)):
        assert long_line[-(idx + 1)] == p
    with pytest.raises(IndexError):
        _ = long_line[-99]
    # Slicing
    start_index = 1
    points = long_line[start_index:start_index+2]
    for idx, p in enumerate(points):
        assert p == long_line[start_index+idx]


def test_centroid(long_line: LineString) -> None:
    assert long_line.centroid() == long_line.centroid(True)


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_vertical_centroid(
    closed_vertical_line: LineString, compute_2d_area: bool
) -> None:
    assert (
        closed_vertical_line.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area
