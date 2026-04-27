import icontract
import pytest

from pysfcgal.sfcgal import LineString, Polygon, PolyhedralSurface


@pytest.fixture
def polyhedralsurface(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [
            [[c000, c100, c010]],
            [[c000, c001, c100]],
            [[c000, c010, c001]],
            [[c100, c001, c010]],
        ]
    )


@pytest.fixture
def other_polyhedralsurface(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [[[c000, c100, c010]], [[c000, c100, c001]], [[c000, c010, c001]]]
    )


@pytest.fixture
def polyhedralsurface_unordered(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [
            [[c100, c001, c010]],
            [[c000, c100, c010]],
            [[c100, c000, c001]],
            [[c000, c010, c001]],
        ]
    )


@pytest.fixture
def expected_polygons(c000, c100, c010, c001):
    yield [
        Polygon([c000, c100, c010]),
        Polygon([c000, c001, c100]),
        Polygon([c000, c010, c001]),
        Polygon([c100, c001, c010]),
    ]


def test_polyhedralsurface_len(polyhedralsurface):
    assert len(polyhedralsurface) == 4


def test_polyhedralsurface_iteration(polyhedralsurface, expected_polygons):
    for polygon, expected_polygon in zip(polyhedralsurface, expected_polygons):
        assert polygon == expected_polygon


def test_polyhedralsurface_indexing(polyhedralsurface, expected_polygons):
    for idx in range(len(polyhedralsurface)):
        assert polyhedralsurface[idx] == expected_polygons[idx]
    assert polyhedralsurface[-1] == expected_polygons[-1]
    assert polyhedralsurface[1:3] == expected_polygons[1:3]


def test_polyhedralsurface_equality(
    polyhedralsurface, other_polyhedralsurface, polyhedralsurface_unordered
):
    assert polyhedralsurface != other_polyhedralsurface
    assert polyhedralsurface != polyhedralsurface_unordered


def test_polyhedralsurface_validity(polyhedralsurface, other_polyhedralsurface) -> None:
    assert polyhedralsurface.is_valid()
    assert not other_polyhedralsurface.is_valid()
    assert not other_polyhedralsurface.validity_flag
    invalidity_reason, _ = other_polyhedralsurface.is_valid_detail()
    assert invalidity_reason == (
        "inconsistent orientation of PolyhedralSurface detected "
        "at edge 2 (3-0) of polygon 2"
    )
    other_polyhedralsurface.validity_flag = True
    assert other_polyhedralsurface.validity_flag
    assert other_polyhedralsurface.is_valid()
    assert other_polyhedralsurface.is_valid_detail() == (None, None)


def test_polyhedralsurface_to_coordinates(polyhedralsurface, c000, c100, c010, c001):
    assert polyhedralsurface.to_coordinates() == [
        [[c000, c100, c010, c000]],
        [[c000, c001, c100, c000]],
        [[c000, c010, c001, c000]],
        [[c100, c001, c010, c100]],
    ]
    other_phs = PolyhedralSurface.from_coordinates(polyhedralsurface.to_coordinates())
    assert other_phs == polyhedralsurface


def test_to_multipolygon(polyhedralsurface, expected_multipolygon):
    multipoly = polyhedralsurface.to_multipolygon(wrapped=True)
    assert multipoly.geom_type == "MultiPolygon"
    assert multipoly == expected_multipolygon


def test_to_solid():
    coords_str = (
        "((3.0 3.0 0.0,3.0 8.0 0.0,8.0 8.0 0.0,8.0 3.0 0.0"
        ",3.0 3.0 0.0)),"
        "((3.0 3.0 30.0,8.0 3.0 30.0,8.0 8.0 30.0,3.0 8.0 30.0,3.0 3.0 30.0)),"
        "((3.0 3.0 0.0,3.0 3.0 30.0,3.0 8.0 30.0,3.0 8.0 0.0,3.0 3.0 0.0)),"
        "((3.0 8.0 0.0,3.0 8.0 30.0,8.0 8.0 30.0,8.0 8.0 0.0,3.0 8.0 0.0)),"
        "((8.0 8.0 0.0,8.0 8.0 30.0,8.0 3.0 30.0,8.0 3.0 0.0,8.0 8.0 0.0)),"
        "((8.0 3.0 0.0,8.0 3.0 30.0,3.0 3.0 30.0,3.0 3.0 0.0,8.0 3.0 0.0))"
    )

    wkt_poly = f"POLYHEDRALSURFACE Z ({coords_str})"
    poly = PolyhedralSurface.from_wkt(wkt_poly)
    solid = poly.to_solid()
    expected_wkt = f"SOLID Z (({coords_str}))"
    assert solid.to_wkt(1) == expected_wkt


def test_polyhedralsurface_add_polygon(polyhedralsurface, c100, c010, c001):
    new_polygon = Polygon([c010, c100, c001])
    assert len(polyhedralsurface) == 4
    assert new_polygon not in polyhedralsurface

    polyhedralsurface.add_patch(new_polygon)
    assert len(polyhedralsurface) == 5
    assert new_polygon in polyhedralsurface


def test_polyhedralsurface_add_linestring_fails(polyhedralsurface, c100, c010, c001):
    # try to add a linestring to a polyhedral surface
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        polyhedralsurface.add_patch(LineString([c100, c010, c001]))


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_vertical_centroid(
    polyhedralsurface: PolyhedralSurface, compute_2d_area: bool
) -> None:
    assert (
        polyhedralsurface.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area


def test_polyhedralsurface_memory_management(c000, c100, c010, c001):
    first_patch_wkt = "POLYGON Z ((0 0 0,1 0 0,0 1 0,0 0 0))"

    patches = list(PolyhedralSurface(
        [[[c000, c100, c010]], [[c000, c100, c001]], [[c000, c010, c001]]])
    )
    assert patches[0].to_wkt(0) == first_patch_wkt

    first_patch = PolyhedralSurface(
        [[[c000, c100, c010]], [[c000, c100, c001]], [[c000, c010, c001]]]
    )[0]
    assert first_patch.to_wkt(0) == first_patch_wkt


def test_polyhedralsurface_n_edges(polyhedralsurface):
    assert polyhedralsurface.n_edges == 6
    phs = PolyhedralSurface()
    assert phs.n_edges == 0
    expected_n_edges = (3, 5, 6)
    for patch, exp_n_edges in zip(polyhedralsurface, expected_n_edges):
        phs.add_patch(patch)
        assert phs.n_edges == exp_n_edges
