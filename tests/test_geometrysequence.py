from pysfcgal.sfcgal import GeometrySequence, MultiPoint


def test_geometry_sequence_memory_management(c000, c100, c010):
    first_point_wkt = "POINT Z (1 0 0)"

    sequence_list = list(GeometrySequence(MultiPoint((c100, c010, c000))))
    assert sequence_list[0].to_wkt(0) == first_point_wkt

    first_point = GeometrySequence(MultiPoint((c100, c010, c000)))[0]
    assert first_point.to_wkt(0) == first_point_wkt
