import pathlib

import icontract
import pytest

from pysfcgal.geometry import Polygon
from pysfcgal.geometry.collection import MultiLineString
from pysfcgal.geometry.surface import PolyhedralSurface


@pytest.fixture
def square_with_hole_polygon():
    exterior = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]
    interiors = [[(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)]]
    yield Polygon(exterior=exterior, interiors=interiors)


POLYGON_EXPECTED_DATA = pathlib.Path(__file__).parent / "polygon" / "expected_data"
SFCGAL_EXPECTED_DATA = pathlib.Path(__file__).parent / "expected_data"


# ---------------------------------------------------------------------------
# extrude_straight_skeleton
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_basic(polygon1):
    result = polygon1.extrude_straight_skeleton(1.0)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_straight_skeleton_height_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_straight_skeleton(0.0)


# ---------------------------------------------------------------------------
# extrude_polygon_straight_skeleton
# ---------------------------------------------------------------------------

def test_extrude_polygon_straight_skeleton(polygon1):
    result = polygon1.extrude_polygon_straight_skeleton(3.0, 1.0)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_polygon_straight_skeleton_roof_height_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_polygon_straight_skeleton(3.0, 0.0)


# ---------------------------------------------------------------------------
# extrude_straight_skeleton_with_angles
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_with_angles_success(polygon1):
    angles = [[45.0, 45.0, 45.0, 45.0]]
    result = polygon1.extrude_straight_skeleton_with_angles(1.0, angles)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_straight_skeleton_with_angles_height_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_straight_skeleton_with_angles(0.0, [[45.0, 45.0, 45.0, 45.0]])


def test_extrude_straight_skeleton_with_angles_none(polygon1):
    with pytest.raises(TypeError, match="'angles' must be provided"):
        polygon1.extrude_straight_skeleton_with_angles(1.0, None)


def test_extrude_straight_skeleton_with_angles_wrong_ring_count(
    square_with_hole_polygon
):
    with pytest.raises(ValueError, match="Expected 2 rings of angles, but got 1"):
        square_with_hole_polygon.extrude_straight_skeleton_with_angles(
            1.0, [[45.0, 45.0, 45.0, 45.0]]
        )


def test_extrude_straight_skeleton_with_angles_wrong_edge_count(polygon1):
    with pytest.raises(
        ValueError, match="Ring 0 has 4 edges, but 3 angles were provided"
    ):
        polygon1.extrude_straight_skeleton_with_angles(1.0, [[45.0, 45.0, 45.0]])


# ---------------------------------------------------------------------------
# extrude_polygon_straight_skeleton_with_angles
# ---------------------------------------------------------------------------

def test_extrude_polygon_straight_skeleton_with_angles_success(polygon1):
    angles = [[45.0, 45.0, 45.0, 45.0]]
    result = polygon1.extrude_polygon_straight_skeleton_with_angles(3.0, 1.0, angles)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_polygon_straight_skeleton_with_angles_roof_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_polygon_straight_skeleton_with_angles(3.0, 0.0, [[45.0] * 4])


def test_extrude_polygon_straight_skeleton_with_angles_none(polygon1):
    with pytest.raises(TypeError, match="'angles' must be provided"):
        polygon1.extrude_polygon_straight_skeleton_with_angles(3.0, 1.0, None)


def test_extrude_polygon_straight_skeleton_with_angles_wrong_ring_count(
    square_with_hole_polygon
):
    with pytest.raises(ValueError, match="Expected 2 rings of angles, but got 1"):
        square_with_hole_polygon.extrude_polygon_straight_skeleton_with_angles(
            3.0, 1.0, [[45.0] * 4]
        )


def test_extrude_polygon_straight_skeleton_with_angles_wrong_edge_count(polygon1):
    with pytest.raises(
        ValueError, match="Ring 0 has 4 edges, but 3 angles were provided"
    ):
        polygon1.extrude_polygon_straight_skeleton_with_angles(
            3.0, 1.0, [[45.0, 45.0, 45.0]]
        )


# ---------------------------------------------------------------------------
# extrude_straight_skeleton_with_weights
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_with_weights_success(polygon1):
    weights = [[1.0, 1.0, 1.0, 1.0]]
    result = polygon1.extrude_straight_skeleton_with_weights(1.0, weights)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_straight_skeleton_with_weights_height_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_straight_skeleton_with_weights(0.0, [[1.0, 1.0, 1.0, 1.0]])


def test_extrude_straight_skeleton_with_weights_none(polygon1):
    with pytest.raises(TypeError, match="'weights' must be provided"):
        polygon1.extrude_straight_skeleton_with_weights(1.0, None)


def test_extrude_straight_skeleton_with_weights_wrong_ring_count(
    square_with_hole_polygon
):
    with pytest.raises(ValueError, match="Expected 2 rings of weights, but got 1"):
        square_with_hole_polygon.extrude_straight_skeleton_with_weights(
            1.0, [[1.0, 1.0, 1.0, 1.0]]
        )


def test_extrude_straight_skeleton_with_weights_wrong_edge_count(polygon1):
    with pytest.raises(
        ValueError, match="Ring 0 has 4 edges, but 3 weights were provided"
    ):
        polygon1.extrude_straight_skeleton_with_weights(1.0, [[1.0, 1.0, 1.0]])


# ---------------------------------------------------------------------------
# extrude_polygon_straight_skeleton_with_weights
# ---------------------------------------------------------------------------

def test_extrude_polygon_straight_skeleton_with_weights_success(polygon1):
    weights = [[1.0, 1.0, 1.0, 1.0]]
    result = polygon1.extrude_polygon_straight_skeleton_with_weights(3.0, 1.0, weights)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_polygon_straight_skeleton_with_weights_roof_zero(polygon1):
    with pytest.raises(icontract.errors.ViolationError):
        polygon1.extrude_polygon_straight_skeleton_with_weights(3.0, 0.0, [[1.0] * 4])


def test_extrude_polygon_straight_skeleton_with_weights_none(polygon1):
    with pytest.raises(TypeError, match="'weights' must be provided"):
        polygon1.extrude_polygon_straight_skeleton_with_weights(3.0, 1.0, None)


def test_extrude_polygon_straight_skeleton_with_weights_wrong_ring_count(
    square_with_hole_polygon
):
    with pytest.raises(ValueError, match="Expected 2 rings of weights, but got 1"):
        square_with_hole_polygon.extrude_polygon_straight_skeleton_with_weights(
            3.0, 1.0, [[1.0] * 4]
        )


def test_extrude_polygon_straight_skeleton_with_weights_wrong_edge_count(polygon1):
    with pytest.raises(
        ValueError, match="Ring 0 has 4 edges, but 3 weights were provided"
    ):
        polygon1.extrude_polygon_straight_skeleton_with_weights(
            3.0, 1.0, [[1.0, 1.0, 1.0]]
        )


# ---------------------------------------------------------------------------
# Multi-ring polygons
# ---------------------------------------------------------------------------

def test_extrude_with_angles_multi_ring(square_with_hole_polygon):
    # exterior: 4 edges, interior: 4 edges
    angles = [[45.0, 45.0, 45.0, 45.0], [45.0, 45.0, 45.0, 45.0]]
    result = square_with_hole_polygon.extrude_straight_skeleton_with_angles(1.0, angles)
    assert isinstance(result, PolyhedralSurface)


def test_extrude_with_weights_multi_ring(square_with_hole_polygon):
    weights = [[1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]]
    result = square_with_hole_polygon.extrude_straight_skeleton_with_weights(
        1.0, weights
    )
    assert isinstance(result, PolyhedralSurface)


# ---------------------------------------------------------------------------
# Empty polygon handling for angles/weights variants
# ---------------------------------------------------------------------------

def test_extrude_straight_skeleton_with_angles_empty_polygon():
    # An empty polygon has an empty exterior ring; _validate_ring_values must
    # raise a clear ValueError instead of an IndexError.
    poly = Polygon()
    with pytest.raises(ValueError, match="Ring 0 is empty"):
        poly.extrude_straight_skeleton_with_angles(1.0, [[]])


def test_extrude_straight_skeleton_with_weights_empty_polygon():
    poly = Polygon()
    with pytest.raises(ValueError, match="Ring 0 is empty"):
        poly.extrude_straight_skeleton_with_weights(1.0, [[]])


def test_extrude_polygon_straight_skeleton_with_angles_empty_polygon():
    poly = Polygon()
    with pytest.raises(ValueError, match="Ring 0 is empty"):
        poly.extrude_polygon_straight_skeleton_with_angles(3.0, 1.0, [[]])


def test_extrude_polygon_straight_skeleton_with_weights_empty_polygon():
    poly = Polygon()
    with pytest.raises(ValueError, match="Ring 0 is empty"):
        poly.extrude_polygon_straight_skeleton_with_weights(3.0, 1.0, [[]])


# ---------------------------------------------------------------------------
# Other straight skeleton methods
# ---------------------------------------------------------------------------

def test_straight_skeleton_returns_multilinestring(polygon1):
    result = polygon1.straight_skeleton()
    assert result is not None
    assert isinstance(result, MultiLineString)


def test_straight_skeleton_partition_polygon(polygon1):
    result = polygon1.straight_skeleton_partition()
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
    # Acute angles
    roof = heptagon_building_footprint.extrude_straight_skeleton_with_angles(
        height=10, angles=[[90, 90, 45, 30, 30, 15, 15]]
    )
    assert isinstance(roof, PolyhedralSurface)
    expected_wkt = (
        POLYGON_EXPECTED_DATA / "straight_skeleton_extrusion_acute_angles.wkt"
    ).read_text().strip()
    assert roof.to_wkt(2) == expected_wkt

    # Obtuse angles (> 90°) cause the straight-skeleton extrusion to project
    # faces *outside* the original polygon footprint, producing coordinates
    # with negative Y values and an apex row beyond the polygon boundary.
    # The expected output reflects SFCGAL's correct behaviour for obtuse inputs
    roof = heptagon_building_footprint.extrude_straight_skeleton_with_angles(
        height=10, angles=[[100, 90, 145, 145, 145, 145, 145]]
    )
    assert isinstance(roof, PolyhedralSurface)
    expected_wkt = (
        POLYGON_EXPECTED_DATA / "straight_skeleton_extrusion_obtuse_angles.wkt"
    ).read_text().strip()
    assert roof.to_wkt(2) == expected_wkt


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
