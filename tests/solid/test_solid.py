import icontract
import pytest

from pysfcgal import LineString, PolyhedralSurface, Solid


def test_solid(
    solid, expected_polyhedralsurfaces, solid_without_holes, solid_unordered
):
    assert solid.n_shells == 3
    assert len(solid) == 3
    # iteration
    for shell, expected_polyhedral in zip(solid, expected_polyhedralsurfaces):
        assert shell == expected_polyhedral
    # indexing
    for idx in range(solid.n_shells):
        solid[idx] == expected_polyhedralsurfaces[idx]
    solid[-1] == expected_polyhedralsurfaces[-1]
    solid[1:3] == expected_polyhedralsurfaces[1:3]
    # equality
    assert solid != solid_without_holes
    assert solid != solid_unordered


def test_solid_to_polyhedralsurface(solid, composed_polyhedralsurface):
    phs = solid.to_polyhedralsurface(wrapped=True)
    assert not phs.is_valid()  # PolyhedralSurface with interior shells
    assert phs.geom_type == "PolyhedralSurface"
    assert phs == composed_polyhedralsurface


def test_solid_to_coordinates(solid, points_ext_1, points_int_1, points_int_2):
    assert solid.to_coordinates() == [points_ext_1, points_int_1, points_int_2]
    other_solid = Solid.from_coordinates(solid.to_coordinates())
    assert other_solid == solid


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_tessellate_3d_solid(solid_without_holes):
    assert solid_without_holes.is_valid()
    tessellation = solid_without_holes.tessellate()
    assert tessellation.geom_type == "GeometryCollection"

    tessellation_3d = solid_without_holes.tessellate_3d()
    assert tessellation == tessellation_3d


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_tessellate_3d_polyhedralsurface(solid):
    """Solid is not valid, we test the tessellate on its shells."""
    assert not solid.is_valid()
    for shell in solid:
        assert shell.is_valid()
        tessellation = shell.tessellate()
        assert tessellation.geom_type == "TriangulatedSurface"

        tessellation_3d = shell.tessellate_3d()
        assert tessellation == tessellation_3d


def test_solid_set_exterior_shell(solid, points_ext_1, points_ext_2):
    new_exterior_shell = PolyhedralSurface(points_ext_2)

    assert solid.n_shells == 3
    assert solid.shells[0] == PolyhedralSurface(points_ext_1)
    assert new_exterior_shell not in solid

    solid.set_exterior_shell(new_exterior_shell)
    assert solid.n_shells == 3
    assert solid.shells[0] == new_exterior_shell


def test_solid_set_exterior_shell_from_linestring_fails(solid, c000, c100, c010):
    # try to set a linestring as exterior shell
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        solid.set_exterior_shell(LineString([c000, c100, c010]))


def test_solid_add_interior_shell(solid, points_ext_2):
    new_interior_shell = PolyhedralSurface(points_ext_2)

    assert solid.n_shells == 3
    assert new_interior_shell not in solid

    solid.add_interior_shell(new_interior_shell)
    assert solid.n_shells == 4
    assert solid.shells[3] == new_interior_shell


def test_solid_add_interior_shell_from_linestring_fails(solid, c000, c100, c010):
    # try to add a linestring as an interior shell
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        solid.add_interior_shell(LineString([c000, c100, c010]))


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_vertical_centroid(
    solid_without_holes: Solid, compute_2d_area: bool
) -> None:
    assert (
        solid_without_holes.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area


def test_solid_memory_management(points_ext_1, points_int_1, points_int_2):
    first_shell_wkt = (
        "POLYHEDRALSURFACE Z (((0 0 0,0 10 0,10 10 0,10 0 0,0 0 0)),"
        "((0 0 10,10 0 10,10 10 10,0 10 10,0 0 10)),"
        "((0 0 0,0 0 10,0 10 10,0 10 0,0 0 0)),"
        "((0 10 0,0 10 10,10 10 10,10 10 0,0 10 0)),"
        "((10 10 0,10 10 10,10 0 10,10 0 0,10 10 0)),"
        "((10 0 0,10 0 10,0 0 10,0 0 0,10 0 0)))"
    )

    shells = list(Solid([points_ext_1, points_int_1, points_int_2]))
    assert shells[0].to_wkt(0) == first_shell_wkt

    first_shell = Solid([points_ext_1, points_int_1, points_int_2])[0]
    assert first_shell.to_wkt(0) == first_shell_wkt
