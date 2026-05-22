import pathlib

import pytest

from pysfcgal import Polygon, PolyhedralSurface, Solid
from pysfcgal.roof import (RoofType, generate_flat_roof, generate_gable_roof,
                           generate_hipped_roof, generate_roof,
                           generate_skillion_roof)

EXPECTED_DATA_PATH = pathlib.Path(__file__).parent.resolve() / "expected_data"


@pytest.fixture
def rectangle_building_footprint():
    yield Polygon.from_coordinates([[(0, 0), (4, 0), (4, 10), (0, 10), (0, 0)]])


@pytest.mark.parametrize(
    "height,expected_wkt_path",
    [(0, "flat_roof_no_height.wkt"), (2.8, "flat_roof_with_height.wkt")],
)
def test_flat_roof_generation(
    polygon1: Polygon, height: float, expected_wkt_path: str
) -> None:
    roof = generate_flat_roof(polygon1, height)
    assert isinstance(roof, Solid)
    expected_wkt = (EXPECTED_DATA_PATH / expected_wkt_path).read_text().strip()
    assert roof.to_wkt(1) == expected_wkt

    same_roof = generate_roof(polygon1, RoofType.FLAT, height=height)
    assert roof == same_roof

    # flat roof is an alias for Polygon.extrude
    assert roof == polygon1.extrude(extrude_x=0, extrude_y=0, extrude_z=height)


def test_hipped_roof_generation(rectangle_building_footprint: Polygon) -> None:
    height = 5.3
    roof = generate_hipped_roof(rectangle_building_footprint, height)
    assert isinstance(roof, PolyhedralSurface)
    expected_wkt = (EXPECTED_DATA_PATH / "hipped_roof.wkt").read_text().strip()
    assert roof.to_wkt(0) == expected_wkt

    same_roof = generate_roof(
        rectangle_building_footprint, RoofType.HIPPED, height=height
    )
    assert roof == same_roof

    # hipped roof is alias for Polygon.extrude_straight_skeleton
    assert roof == rectangle_building_footprint.extrude_straight_skeleton(height)


def test_gable_roof_generation(rectangle_building_footprint: Polygon) -> None:
    height = 5.3
    slope_angle = 29.7
    roof = generate_gable_roof(rectangle_building_footprint, height, slope_angle)
    assert isinstance(roof, PolyhedralSurface)
    expected_wkt = (EXPECTED_DATA_PATH / "gable_roof.wkt").read_text().strip()
    assert roof.to_wkt(0) == expected_wkt

    same_roof = generate_roof(
        rectangle_building_footprint,
        RoofType.GABLE,
        height=height,
        slope_angle=slope_angle,
    )
    assert roof == same_roof


@pytest.mark.parametrize(
    "height,slope_angle,primary_edge_index,expected_wkt_path",
    [
        (5.3, 29.7, 1, "skillion_roof_index_1.wkt"),
        (3.6, 19.7, 2, "skillion_roof_index_2.wkt"),
    ],
)
def test_skillion_roof_generation(
    rectangle_building_footprint: Polygon,
    height: float,
    slope_angle: float,
    primary_edge_index: int,
    expected_wkt_path: str,
) -> None:
    roof = generate_skillion_roof(
        rectangle_building_footprint,
        height=height,
        slope_angle=slope_angle,
        primary_edge_index=primary_edge_index,
    )
    assert isinstance(roof, PolyhedralSurface)
    expected_wkt = (EXPECTED_DATA_PATH / expected_wkt_path).read_text().strip()
    assert roof.to_wkt(0) == expected_wkt

    same_roof = generate_roof(
        rectangle_building_footprint,
        RoofType.SKILLION,
        height=height,
        slope_angle=slope_angle,
        primary_edge_index=primary_edge_index,
    )
    assert roof == same_roof
