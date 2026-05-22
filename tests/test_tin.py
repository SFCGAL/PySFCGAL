import icontract
import pytest

from pysfcgal import LineString, Tin, Triangle


@pytest.fixture
def expected_triangles(c000, c100, c010, c001):
    yield [
        Triangle([c000, c100, c010]),
        Triangle([c000, c001, c100]),
        Triangle([c000, c010, c001]),
        Triangle([c100, c001, c010]),
    ]


@pytest.fixture
def tin_coordinates(c000, c100, c010, c001):
    yield [
        [c000, c100, c010], [c000, c001, c100], [c000, c010, c001], [c100, c001, c010]
    ]


@pytest.fixture
def tin(tin_coordinates):
    yield Tin(tin_coordinates)


@pytest.fixture
def tin_unclosed(c000, c100, c010, c001):
    yield Tin([[c000, c100, c010], [c000, c100, c001], [c000, c010, c001]])


@pytest.fixture
def tin_unordered(c000, c100, c010, c001):
    yield Tin([[c000, c100, c010], [c000, c100, c001], [c000, c010, c001]])


def test_tin(tin, expected_triangles, tin_unclosed, tin_unordered):
    assert len(tin) == 4
    # iteration
    for triangle, expected_triangle in zip(tin, expected_triangles):
        assert triangle == expected_triangle
    # indexing
    for idx in range(len(tin)):
        assert tin[idx] == expected_triangles[idx]
    assert tin[-1] == expected_triangles[-1]
    assert tin[1:3] == expected_triangles[1:3]
    # equality
    assert tin != tin_unclosed
    assert tin != tin_unordered


def test_tin_validity(tin, tin_unclosed):
    """One may bypass the validity check by setting a validity flag.
    """
    assert tin.is_valid()
    assert not tin_unclosed.is_valid()
    assert not tin_unclosed.validity_flag
    invalidity_reason, _ = tin_unclosed.is_valid_detail()
    assert invalidity_reason == (
        "inconsistent orientation of PolyhedralSurface detected "
        "at edge 2 (3-0) of polygon 2"
    )
    tin_unclosed.validity_flag = True
    assert tin_unclosed.validity_flag
    assert tin_unclosed.is_valid()
    assert tin_unclosed.is_valid_detail() == (None, None)


def test_tin_wkt(tin, tin_coordinates):
    assert tin.to_wkt(0) == (
        "TIN Z ("
        "((0 0 0,1 0 0,0 1 0,0 0 0)),"
        "((0 0 0,0 0 1,1 0 0,0 0 0)),"
        "((0 0 0,0 1 0,0 0 1,0 0 0)),"
        "((1 0 0,0 0 1,0 1 0,1 0 0)))"
    )


def test_tin_to_coordinates(tin, tin_coordinates):
    assert tin.to_coordinates() == tin_coordinates
    cloned_tin = Tin(tin_coordinates)
    assert cloned_tin == tin
    other_tin = Tin.from_coordinates(tin.to_coordinates())
    assert other_tin == tin


def test_tin_to_multipolygon(tin, expected_multipolygon):
    multipoly = tin.to_multipolygon(wrapped=True)
    assert multipoly.geom_type == "MultiPolygon"
    assert multipoly == expected_multipolygon


def test_tin_add_patch(tin, c100, c010, c001):
    new_triangle = Triangle([c010, c100, c001])
    assert len(tin) == 4
    assert new_triangle not in tin

    tin.add_patch(new_triangle)
    assert len(tin) == 5
    assert new_triangle in tin


def test_tin_add_linestring_fails(tin, c000, c100, c010):
    # try to add a linestring to a multipoint
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        tin.add_patch(LineString([c000, c100, c010]))


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_centroid(
    tin: Tin, compute_2d_area: bool
) -> None:
    assert (tin.centroid(compute_2d_area) is not None) ^ compute_2d_area


def test_tin_memory_management(tin_coordinates):
    first_triangle_wkt = "TRIANGLE Z ((0 0 0,1 0 0,0 1 0,0 0 0))"

    triangles_list = list(Tin(tin_coordinates))
    assert triangles_list[0].to_wkt(0) == first_triangle_wkt

    first_triangle = Tin(tin_coordinates)[0]
    assert first_triangle.to_wkt(0) == first_triangle_wkt


def test_tin_n_edges(expected_triangles):
    tin = Tin()
    assert tin.n_edges == 0
    expected_n_edges = (3, 5, 6)
    for patch, exp_n_edges in zip(expected_triangles, expected_n_edges):
        tin.add_patch(patch)
        assert tin.n_edges == exp_n_edges
