from pysfcgal.sfcgal import MultiSolid


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


def test_multisolid_to_dict(multisolid):
    multisolid_data = multisolid.to_dict()
    other_multisolid = MultiSolid.from_dict(multisolid_data)
    assert other_multisolid == multisolid
