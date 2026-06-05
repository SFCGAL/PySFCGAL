import pathlib

import pytest

from pysfcgal.geometry import Polygon
from pysfcgal.geometry.collection import MultiLineString
from pysfcgal.geometry.surface import PolyhedralSurface

POLYGON_EXPECTED_DATA = pathlib.Path(__file__).parent / "polygon" / "expected_data"
SFCGAL_EXPECTED_DATA = pathlib.Path(__file__).parent / "expected_data"

try:
    import icontract
    _PRECONDITION_ERROR = icontract.errors.ViolationError
except ImportError:
    _PRECONDITION_ERROR = ValueError

SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
SQUARE_WITH_HOLE = (
    [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)],       # exterior: CCW
    [[(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)]],      # interior: CW (hole)
)


# ---------------------------------------------------------------------------
# extrude_straight_skeleton
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_basic():
    poly = Polygon(SQUARE)
    result = poly.extrude_straight_skeleton(1.0)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_straight_skeleton_height_zero():
    poly = Polygon(SQUARE)
    with pytest.raises(_PRECONDITION_ERROR):
        poly.extrude_straight_skeleton(0.0)


# ---------------------------------------------------------------------------
# extrude_polygon_straight_skeleton
# ---------------------------------------------------------------------------

def test_extrude_polygon_straight_skeleton():
    poly = Polygon(SQUARE)
    result = poly.extrude_polygon_straight_skeleton(3.0, 1.0)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_polygon_straight_skeleton_roof_height_zero():
    poly = Polygon(SQUARE)
    with pytest.raises(_PRECONDITION_ERROR):
        poly.extrude_polygon_straight_skeleton(3.0, 0.0)


# ---------------------------------------------------------------------------
# extrude_straight_skeleton_with_angles
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_with_angles_success():
    poly = Polygon(SQUARE)
    angles = [[45.0, 45.0, 45.0, 45.0]]
    result = poly.extrude_straight_skeleton_with_angles(1.0, angles)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_straight_skeleton_with_angles_height_zero():
    poly = Polygon(SQUARE)
    with pytest.raises(_PRECONDITION_ERROR):
        poly.extrude_straight_skeleton_with_angles(0.0, [[45.0, 45.0, 45.0, 45.0]])


def test_extrude_straight_skeleton_with_angles_none():
    poly = Polygon(SQUARE)
    with pytest.raises(TypeError, match="'angles' must be provided"):
        poly.extrude_straight_skeleton_with_angles(1.0, None)


def test_extrude_straight_skeleton_with_angles_wrong_ring_count():
    poly = Polygon(*SQUARE_WITH_HOLE)
    with pytest.raises(ValueError, match="Expected 2 rings of angles, but got 1"):
        poly.extrude_straight_skeleton_with_angles(1.0, [[45.0, 45.0, 45.0, 45.0]])


def test_extrude_straight_skeleton_with_angles_wrong_edge_count():
    poly = Polygon(SQUARE)
    with pytest.raises(
        ValueError, match="Ring 0 has 4 edges, but 3 angles were provided"
    ):
        poly.extrude_straight_skeleton_with_angles(1.0, [[45.0, 45.0, 45.0]])


# ---------------------------------------------------------------------------
# Multi-ring polygons
# ---------------------------------------------------------------------------

def test_extrude_with_angles_multi_ring():
    poly = Polygon(*SQUARE_WITH_HOLE)
    # exterior: 4 edges, interior: 4 edges
    angles = [[45.0, 45.0, 45.0, 45.0], [45.0, 45.0, 45.0, 45.0]]
    result = poly.extrude_straight_skeleton_with_angles(1.0, angles)
    assert isinstance(result, PolyhedralSurface)


# ---------------------------------------------------------------------------
# Other straight skeleton methods
# ---------------------------------------------------------------------------

def test_straight_skeleton_returns_multilinestring():
    poly = Polygon(SQUARE)
    result = poly.straight_skeleton()
    assert result is not None
    assert isinstance(result, MultiLineString)


def test_straight_skeleton_partition_polygon():
    poly = Polygon(SQUARE)
    result = poly.straight_skeleton_partition()
    assert result is not None
    assert isinstance(result, PolyhedralSurface)


# ---------------------------------------------------------------------------
# WKT-comparison tests (migrated from test_polygon.py / test_sfcgal.py)
# ---------------------------------------------------------------------------

@pytest.fixture
def heptagon_building_footprint():
    yield Polygon.from_coordinates(
        [[(0, 0), (4, 0), (4, 3), (7, 3), (9, 5), (9, 10), (0, 10), (0, 0)]]
    )


def test_extrude_straight_skeleton_with_angles(
    heptagon_building_footprint: Polygon,
) -> None:
    roof = heptagon_building_footprint.extrude_straight_skeleton_with_angles(
        height=10, angles=[[90, 90, 45, 30, 30, 15, 15]]
    )
    assert isinstance(roof, PolyhedralSurface)
    assert (
        roof.to_wkt(2)
        == (POLYGON_EXPECTED_DATA / "straight_skeleton_extrusion_acute_angles.wkt")
        .read_text()
        .strip()
    )

    # Obtuse angles (> 90°) cause the straight-skeleton extrusion to project
    # faces *outside* the original polygon footprint, producing coordinates
    # with negative Y values and an apex row beyond the polygon boundary.
    # The expected output reflects SFCGAL's correct behaviour for obtuse inputs.
    roof = heptagon_building_footprint.extrude_straight_skeleton_with_angles(
        height=10, angles=[[100, 90, 145, 145, 145, 145, 145]]
    )
    assert isinstance(roof, PolyhedralSurface)
    assert (
        roof.to_wkt(2)
        == (POLYGON_EXPECTED_DATA / "straight_skeleton_extrusion_obtuse_angles.wkt")
        .read_text()
        .strip()
    )


def test_extrude_straight_skeleton_polygon():
    """Inspired from testExtrudeStraightSkeleton SFCGAL unit test"""
    empty_polygon = Polygon()
    assert empty_polygon.is_empty
    empty_res = empty_polygon.extrude_straight_skeleton(2.0)
    assert empty_res.geom_type == "PolyhedralSurface"
    assert empty_res.is_empty

    geom = Polygon.from_wkt("POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ))")
    expected_wkt = (
        SFCGAL_EXPECTED_DATA / "expected_extrude_straight_polygon.wkt"
    ).read_text().strip()
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.to_wkt(2)


def test_extrude_straight_skeleton_polygon_with_hole():
    """Inspired from testExtrudeStraightSkeletonPolygonWithHole SFCGAL unit test"""
    geom = Polygon.from_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        SFCGAL_EXPECTED_DATA / "expected_extrude_straight_polygon_with_hole.wkt"
    ).read_text().strip()
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.to_wkt(2)


def test_extrude_straight_skeleton_building():
    """Inspired from testExtrudeStraightSkeletonGenerateBuilding SFCGAL unit test"""
    empty_polygon = Polygon()
    assert empty_polygon.is_empty
    empty_res = empty_polygon.extrude_polygon_straight_skeleton(9.0, 2.0)
    assert empty_res.geom_type == "PolyhedralSurface"
    assert empty_res.is_empty

    geom = Polygon.from_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        SFCGAL_EXPECTED_DATA / "expected_extrude_straight_polygon_building.wkt"
    ).read_text().strip()
    result = geom.extrude_polygon_straight_skeleton(9.0, 2.0)
    assert result.is_valid()
    assert expected_wkt == result.to_wkt(1)
