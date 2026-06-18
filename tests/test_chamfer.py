import pytest

from pysfcgal import LineString, MultiLineString, Solid
from tests.utils import solid_factory


@pytest.fixture
def cube():
    # Unit cube (0,0,0)-(1,1,1), volume == 1.0
    return solid_factory(0.0)


@pytest.fixture
def bottom_edge():
    # A single bottom edge of the cube
    return LineString([[0, 0, 0], [1, 0, 0]])


@pytest.fixture
def bottom_edges():
    edges = MultiLineString()
    for a, b in (
        ((0, 0, 0), (1, 0, 0)),
        ((1, 0, 0), (1, 1, 0)),
        ((1, 1, 0), (0, 1, 0)),
        ((0, 1, 0), (0, 0, 0)),
    ):
        edges.add_linestring(LineString([list(a), list(b)]))
    return edges


def test_chamfer_cube_bottom_edge(cube, bottom_edge):
    assert cube.is_valid()

    result = cube.chamfer(bottom_edge, 0.1)

    assert result.is_valid()
    assert isinstance(result, Solid)
    assert result.volume < cube.volume
    assert result.volume > 0.98


def test_fillet_cube_bottom_edge(cube, bottom_edge):
    assert cube.is_valid()

    result = cube.fillet(bottom_edge, 0.1, segments=8)

    assert result.is_valid()
    assert isinstance(result, Solid)
    assert result.volume < cube.volume


def test_chamfer_multi_edges(cube, bottom_edges):
    result = cube.chamfer(bottom_edges, 0.1)

    assert result.is_valid()
    assert isinstance(result, Solid)
    assert result.volume < cube.volume


def test_chamfer_asymmetric(cube, bottom_edge):
    symmetric = cube.chamfer(bottom_edge, 0.1)
    asymmetric = cube.chamfer(bottom_edge, 0.1, radius_y=0.2)

    assert asymmetric.is_valid()
    assert isinstance(asymmetric, Solid)
    # A wider second leg removes more material than the symmetric chamfer
    assert asymmetric.volume < symmetric.volume
