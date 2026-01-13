import pytest


@pytest.fixture
def big_ring_ccw():
    yield [(0., 0.), (10., 0.), (10., 10.), (0., 10.), (0., 0.)]


@pytest.fixture
def ring_around_0_ccw():
    yield [(-1., -1.), (1., -1.), (1., 1.), (-1., 1.), (-1., -1.)]


@pytest.fixture
def small_ring_23_ccw():
    yield [(2., 2.), (3., 2.), (3., 3.), (2., 2.)]


@pytest.fixture
def small_ring_56_cw():
    yield [(5., 5.), (5., 6.), (6., 6.), (5., 5.)]
