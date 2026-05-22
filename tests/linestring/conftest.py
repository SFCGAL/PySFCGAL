import pytest

from pysfcgal import LineString


@pytest.fixture
def lineX(c000, c100):
    yield LineString([c000, c100])


@pytest.fixture
def lineY(c000, c010):
    yield LineString([c000, c010])


@pytest.fixture
def lineZ(c000, c001):
    yield LineString([c000, c001])
