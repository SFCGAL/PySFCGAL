import icontract
import pytest

from pysfcgal import MultiSolid, Solid


def test_multisolid_iteration(multisolid, expected_solids):
    for polygon, expected_polygon in zip(multisolid, expected_solids):
        assert polygon == expected_polygon


def test_multisolid_indexing(multisolid, expected_solids):
    for idx in range(len(multisolid)):
        assert multisolid[idx] == expected_solids[idx]
    assert multisolid[-1] == expected_solids[-1]
    assert multisolid[1:3] == expected_solids[1:3]


def test_multisolid_equality(
    multisolid, other_multisolid, multisolid_unordered
):
    assert multisolid != other_multisolid
    assert multisolid != multisolid_unordered  # the order is important


def test_multisolid_to_coordinates(multisolid, expected_solids):
    assert multisolid.to_coordinates() == [
        es.to_coordinates() for es in expected_solids
    ]
    cloned_multisolid = MultiSolid(multisolid.to_coordinates())
    assert cloned_multisolid == multisolid
    other_multisolid = MultiSolid.from_coordinates(multisolid.to_coordinates())
    assert other_multisolid == multisolid


def test_multisolid_add_solid(points_int_1, multisolid, point010):
    solid = Solid([points_int_1])
    assert len(multisolid) == 3
    assert solid not in multisolid

    multisolid.add_solid(solid)
    assert len(multisolid) == 4
    assert solid in multisolid


def test_multisolid_add_point_fails(multisolid, point010):
    # try to add a point to a multisolid
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        multisolid.add_solid(point010)


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_vertical_centroid(
    solid_without_holes: Solid, compute_2d_area: bool
) -> None:
    multisolid = MultiSolid()
    multisolid.add_solid(solid_without_holes)
    assert (
        solid_without_holes.centroid(compute_2d_area) is not None
    ) ^ compute_2d_area
