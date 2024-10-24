import pytest

from pysfcgal.sfcgal import MultiLineString


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


def test_multilinestring_to_dict(multilinestring):
    multilinestring_data = multilinestring.to_dict()
    other_multilinestring = MultiLineString.from_dict(multilinestring_data)
    assert other_multilinestring == multilinestring
