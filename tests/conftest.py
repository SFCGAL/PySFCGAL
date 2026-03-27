import shutil
import tempfile
from pathlib import Path

import pytest

from pysfcgal.sfcgal import MultiPolygon, Point


@pytest.fixture
def tmp_test_dir():
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def c000():
    yield (0., 0., 0.)


@pytest.fixture
def c100():
    yield (1., 0., 0.)


@pytest.fixture
def c010():
    yield (0., 1., 0.)


@pytest.fixture
def c001():
    yield (0., 0., 1.)


@pytest.fixture
def point000(c000):
    yield Point(*c000)


@pytest.fixture
def point100(c100):
    yield Point(*c100)


@pytest.fixture
def point010(c010):
    yield Point(*c010)


@pytest.fixture
def point001(c001):
    yield Point(*c001)


# MultiPoint/Triangle fixtures
@pytest.fixture
def expected_points(point000, point100, point010):
    yield [point000, point100, point010]


# PolyhedraSurface / TIN fixtures
@pytest.fixture
def expected_multipolygon(c000, c100, c010, c001):
    yield MultiPolygon(
        [
            [[c000, c100, c010]],
            [[c000, c001, c100]],
            [[c000, c010, c001]],
            [[c100, c001, c010]],
        ]
    )
