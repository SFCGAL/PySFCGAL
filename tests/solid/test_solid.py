import icontract
import pytest

from pysfcgal.sfcgal import LineString, PolyhedralSurface, Solid


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


def test_solid_to_dict(solid):
    solid_data = solid.to_dict()
    other_solid = Solid.from_dict(solid_data)
    assert other_solid == solid


def test_tessellate_3d_solid(solid_without_holes):
    assert solid_without_holes.is_valid()
    tessellation = solid_without_holes.tessellate_3d()
    assert tessellation.geom_type == "GeometryCollection"


def test_tessellate_3d_polyhedralsurface(solid):
    """Solid is not valid, we test the tessellate on its shells."""
    assert not solid.is_valid()
    for shell in solid:
        assert shell.is_valid()
        tessellation = shell.tessellate_3d()
        assert tessellation.geom_type == "TIN"


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
