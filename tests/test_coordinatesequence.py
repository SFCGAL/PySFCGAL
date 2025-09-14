from pysfcgal.sfcgal import CoordinateSequence, LineString


def test_coordinate_sequence_memory_management():
    sequence_pt = CoordinateSequence(LineString(((0, 0), (1, 0), (5, 2))))[0]
    assert sequence_pt == (0.0, 0.0)
