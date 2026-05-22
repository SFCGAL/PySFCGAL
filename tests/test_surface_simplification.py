"""Test the surface simplification algorithms.

The algorithms are tested regarding different strategies and stop predicates.

"""

from pathlib import Path

import icontract
import pytest

from pysfcgal import Geometry, Tin
from pysfcgal.geometry.simplification import SimplificationStrategy


@pytest.fixture
def bunny_geom(fixture_dir: Path) -> Tin:
    """A valid SFCGAL triangulated surface representing a tiny bunny.

    The validity flag is set to True in order to avoid costly validation checks.

    """
    geom = Geometry.read_obj(str(fixture_dir / "bunny.obj"))
    geom.validity_flag = True
    yield geom


@pytest.fixture
def teddy_geom(fixture_dir: Path) -> Tin:
    """A SFCGAL triangulated surface representing a teddy bear.

    The resulting triangulated surface is not valid according to SFCGAL.

    """
    geom = Geometry.read_obj(str(fixture_dir / "teddy.obj"))
    yield geom


def test_simplify_surface_no_param(bunny_geom):
    assert bunny_geom.simplify_surface() is None


def test_simplify_surface_no_edge(bunny_geom):
    with pytest.raises(
        icontract.errors.ViolationError,
        match=".*edge_count is None or edge_count > 0.*",
    ):
        bunny_geom.simplify_surface(edge_count=0)


def test_simplify_surface_no_edge_ratio(bunny_geom):
    with pytest.raises(
        icontract.errors.ViolationError,
        match=r".*edge_ratio is None or \(edge_ratio > 0 and edge_ratio < 1\).*",
    ):
        bunny_geom.simplify_surface(edge_ratio=0)


def test_simplify_surface_full_edge_ratio(bunny_geom):
    with pytest.raises(
        icontract.errors.ViolationError,
        match=r".*edge_ratio is None or \(edge_ratio > 0 and edge_ratio < 1\).*",
    ):
        bunny_geom.simplify_surface(edge_ratio=1)


def test_simplify_surface_too_much_edges(bunny_geom):
    nb_edges = bunny_geom.n_edges
    ssgeom = bunny_geom.simplify_surface(edge_count=nb_edges+1)
    assert len(ssgeom) == len(bunny_geom)
    assert ssgeom.n_edges == nb_edges
    assert ssgeom.covers_3d(bunny_geom)


@pytest.mark.parametrize(
    "strategy", SimplificationStrategy, ids=[
        strategy.label for strategy in SimplificationStrategy
    ]
)
@pytest.mark.parametrize(
    # the input geometry contains 7473 edges
    "edge_count", [1800, 3600, 5400]
)
def test_simplify_surface_edge_count(strategy, edge_count, bunny_geom):
    ssgeom = bunny_geom.simplify_surface(edge_count=edge_count, strategy=strategy.value)
    assert ssgeom.n_edges < edge_count


@pytest.mark.parametrize(
    "strategy", SimplificationStrategy, ids=[
        strategy.label for strategy in SimplificationStrategy
    ]
)
@pytest.mark.parametrize(
    "ratio", [0.25, 0.5, 0.75]
)
def test_simplify_surface_edge_count_ratio(strategy, ratio, bunny_geom):
    ssgeom = bunny_geom.simplify_surface(edge_ratio=ratio, strategy=strategy.value)
    assert ssgeom.n_edges < bunny_geom.n_edges * ratio


def test_simplify_surface_invalid_geom(teddy_geom):
    """The surface simplification can't work on invalid geometries.

    However we use the validity flag to bypass the validity check, and undertake the
    simplification.

    No miracle though, the output geometry is invalid, as the input geometry is.
    """
    with pytest.raises(
        icontract.errors.ViolationError, match=r".*self.is_valid\(\) was False.*"
    ):
        ssgeom = teddy_geom.simplify_surface(edge_ratio=0.5)

    # After flagging the geometry validity, that's OK
    teddy_geom.validity_flag = True
    ssgeom = teddy_geom.simplify_surface(edge_ratio=0.5)
    # the validity of the output is impacted by the input geometry flag
    assert ssgeom.is_valid()
    assert ssgeom.validity_flag
    # under the hood, the output geometry is invalid
    ssgeom.validity_flag = False
    assert not ssgeom.is_valid()
