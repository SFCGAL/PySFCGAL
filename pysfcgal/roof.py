"""The `roof` module provides functions to generate 3D roof from a footprint."""

from __future__ import annotations

import typing
from enum import IntEnum
from typing import Optional, Type

from ._contracts import cond_icontract
from ._sfcgal import lib

if typing.TYPE_CHECKING:
    from .geometry import Polygon

from .geometry import Geometry


class RoofType(IntEnum):
    label: str

    FLAT = 0, "Flat"
    HIPPED = 1, "Hipped"
    SKILLION = 2, "Skillion"
    GABLE = 3, "Gable"

    def __new__(cls: Type["RoofType"], value: int, label: str) -> "RoofType":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return f"{self.label} ({self.value})"


@cond_icontract(
    lambda footprint, height: (
        footprint.is_valid() and footprint.geom_type == "Polygon" and height >= 0
    ),
    "require",
)
def generate_flat_roof(footprint: Polygon, height: float) -> Optional[Geometry]:
    """Creates a flat roof from the current footprint geometry.
    This is an alias for Polygon.extrude(extrude_z=height).

    Parameters:
    -----------
    height : float
        The roof height.

    Returns
    -------
    Geometry or None
        A 3D geometry representing the building with a flat roof
        applied, or None if the roof could not be generated.
    """
    roof_geom = lib.sfcgal_geometry_generate_flat_roof(footprint._geom, height)
    return Geometry.from_sfcgal_geometry(roof_geom)


@cond_icontract(
    lambda footprint, height: (
        footprint.is_valid() and footprint.geom_type == "Polygon" and height > 0
    ),
    "require",
)
def generate_hipped_roof(footprint: Polygon, height: float) -> Optional[Geometry]:
    """Creates a hipped roof from the current footprint geometry.
    This is an alias for Polygon.extrude_straight_skeleton(height).

    Parameters:
    -----------
    height : float
        The roof height.

    Returns
    -------
    Geometry or None
        A 3D geometry representing the building with a hipped roof
        applied, or None if the roof could not be generated.
    """
    roof_geom = lib.sfcgal_geometry_generate_hipped_roof(footprint._geom, height)
    return Geometry.from_sfcgal_geometry(roof_geom)


@cond_icontract(
    lambda footprint, height, slope_angle: (
        footprint.is_valid()
        and footprint.geom_type == "Polygon"
        and height > 0
        and 0 < slope_angle < 90
    ),
    "require",
)
def generate_gable_roof(
    footprint: Polygon, height: float, slope_angle: float
) -> Optional[Geometry]:
    """Creates a gable roof (dual symmetric slopes) from the current footprint
    geometry.
    Automatically detects gable ends (shortest edges becomes vertical).

    Parameters:
    -----------
    height : float
        The flat roof height.
    slope_angle : float
        The roof slope angle for non-gable edges in degrees.

    Returns
    -------
    Geometry or None
        A 3D geometry representing the building with a gable roof
        applied, or None if the roof could not be generated.
    """
    roof_geom = lib.sfcgal_geometry_generate_gable_roof(
        footprint._geom, height, slope_angle
    )
    return Geometry.from_sfcgal_geometry(roof_geom)


@cond_icontract(
    lambda footprint, height, slope_angle, primary_edge_index: (
        footprint.is_valid()
        and footprint.geom_type == "Polygon"
        and height > 0
        and 0 < slope_angle < 90
        and primary_edge_index >= 0
    ),
    "require",
)
def generate_skillion_roof(
    footprint: Polygon, height: float, slope_angle: float, primary_edge_index: int
) -> Optional[Geometry]:
    """Creates a skillion (mono-pitched) roof from the current footprint geometry.

    Parameters:
    -----------
    height : float
        The flat roof height.
    slope_angle : float
        The roof slope angle in degrees.
    primary_edge_index : int
        The edge index at which the roof begins to rise.

    Returns
    -------
    Geometry or None
        A 3D geometry representing the building with a skillion roof
        applied, or None if the roof could not be generated.
    """
    roof_geom = lib.sfcgal_geometry_generate_skillion_roof(
        footprint._geom, height, slope_angle, primary_edge_index
    )
    return Geometry.from_sfcgal_geometry(roof_geom)


@cond_icontract(
    lambda footprint, roof_type, height, slope_angle, primary_edge_index: (
        footprint.is_valid()
        and isinstance(roof_type, RoofType)
        and footprint.geom_type == "Polygon"
        and height >= 0
        and 0 < slope_angle < 90
        and primary_edge_index >= 0
    ),
    "require",
)
def generate_roof(
    footprint: Polygon,
    roof_type: RoofType,
    height: float = 3.0,
    slope_angle: float = 30.0,
    primary_edge_index: int = 0,
) -> Optional[Geometry]:
    """Creates a roof from the current footprint geometry based on the
    specified roof type.

    Parameters
    ----------
    footprint : Polygon
        The 2D base polygon representing the building footprint.
    roof_type : RoofType
        The type of roof to generate (e.g. gabled, hipped, skillion).
    height : float, optional
        The flat roof height, by default 3.0.
    slope_angle : float, optional
        The roof slope angle in degrees, by default 30.0.
    primary_edge_index : int, optional
        The edge index at which the roof begins to rise, by default 0.

    Returns
    -------
    Geometry or None
        A 3D solid geometry of the building topped with the requested roof
        type, or None if the roof could not be generated.
    """
    roof_geom = lib.sfcgal_geometry_generate_roof(
        footprint._geom, roof_type.value, slope_angle, height, primary_edge_index
    )
    return Geometry.from_sfcgal_geometry(roof_geom)
