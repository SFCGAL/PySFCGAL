import pytest

from pysfcgal import Geometry


@pytest.mark.parametrize(
    "base, source, tolerance, expected_wkt",
    [
        [
            "POLYGON((0 0, 0 5, 5 5, 5 0, 0 0))",
            "POINT(0.001 2.50001)",
            0.01,
            (
                "POLYGON ((0.00 0.00,0.00 2.50,0.00 5.00,5.00 5.00,5.00 0.00,"
                "0.00 0.00))"
            ),
        ],
        [
            "POLYGON((0 0, 0 5, 5 5, 5 0, 0 0))",
            "POINT(0.001 2.50001)",
            0.0000001,
            (
                "POLYGON ((0.00 0.00,0.00 5.00,5.00 5.00,5.00 0.00,0.00 0.00))"
            ),
        ],
        [
            "LINESTRING(0 0, 0 5, 5 5, 5 0, 0 0)",
            "POINT(0.001 2.50001)",
            0.01,
            (
                "LINESTRING (0.00 0.00,0.00 2.50,0.00 5.00,5.00 5.00,5.00 0.00,"
                "0.00 0.00)"
            ),
        ],
        [
            "LINESTRING(0 0, 0 5, 5 5, 5 0, 0 0)",
            "POINT(0.001 2.50001)",
            0.0000001,
            (
                "LINESTRING (0.00 0.00,0.00 5.00,5.00 5.00,5.00 0.00,0.00 0.00)"
            ),
        ],
        [
            "POLYGON((0 0, 0 5, 5 5, 5 0, 0 0))",
            "LINESTRING(0.001 2.50001, 2.50001 4.999, 5 2.5, 2.49999 0.0001)",
            0.01,
            (
                "POLYGON ((0.00 0.00,0.00 2.50,0.00 5.00,2.50 5.00,5.00 5.00,"
                "5.00 2.50,5.00 0.00,2.50 0.00,0.00 0.00))"
            ),
        ],
    ]
)
def test_insert_points_within_tolerance(base, source, tolerance, expected_wkt):
    geom_a = Geometry.from_wkt(base)
    geom_b = Geometry.from_wkt(source)
    assert geom_a.is_valid()
    assert geom_b.is_valid()
    result = geom_a.insert_points_within_tolerance(geom_b, tolerance)
    assert result.geom_type == geom_a.geom_type
    assert result.to_wkt(2) == expected_wkt
