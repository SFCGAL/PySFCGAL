"""Simple Feature Point geometries."""


from __future__ import annotations

import math
import typing
from typing import Optional, Tuple, Union

if typing.TYPE_CHECKING:
    from typing_extensions import TypeAlias

from .._contracts import cond_icontract
from .._sfcgal import ffi, lib
from ..exceptions import DimensionError
from .geometry import Geometry

__all__ = ["Point"]


class Point(Geometry):
    """Point

    Attributes
    ----------
    _owned : bool, default True
        If True, the Python geometry owns the low-level SFCGAL geometry, which is
        removed when the Python structure is cleaned by the garbage collector.
    _geom : _cffi_backend._CDatabase
        SFCGAL point associated to the Point instance. The operations on the geometry
        are done at the SFCGAL lower level.
    """

    Coord: TypeAlias = Optional[Union[int, float]]

    def __init__(
        self, x: Coord = None, y: Coord = None, z: Coord = None, m: Coord = None
    ):
        self._geom = self.sfcgal_geom_from_coordinates([x, y, z, m])

    def __eq__(self, other: object) -> bool:
        """Two points are equals if their dimension and coordinates are equals
        (x, y, z and m).
        """
        if not isinstance(other, Point):
            return False
        are_point_equal = self.x == other.x and self.y == other.y
        if self.has_z and other.has_z:
            are_point_equal &= self.z == other.z
        elif self.has_z ^ other.has_z:
            return False
        if self.has_m and other.has_m:
            are_point_equal &= self.m == other.m
        elif self.has_m ^ other.has_m:
            return False
        return are_point_equal

    @property
    def x(self) -> Coord:
        """Get the x-coordinate of the point.

        Returns
        -------
        float
            The x-coordinate of the point.
        """
        return lib.sfcgal_point_x(self._geom)

    @property
    def y(self) -> Coord:
        """Get the y-coordinate of the point.

        Returns
        -------
        float
            The y-coordinate of the point.
        """
        return lib.sfcgal_point_y(self._geom)

    @property
    def z(self) -> Coord:
        """Get the z-coordinate of the point.

        Raises
        ------
        DimensionError
            If the point has no z coordinate.

        Returns
        -------
        float
            The z-coordinate of the point.
        """
        if lib.sfcgal_geometry_is_3d(self._geom):
            return lib.sfcgal_point_z(self._geom)
        else:
            raise DimensionError("This point has no z coordinate.")

    @property
    def m(self) -> Coord:
        """Get the m-coordinate of the point.

        Raises
        ------
        DimensionError
            If the point has no m coordinate.

        Returns
        -------
        float
            The m-coordinate of the point.
        """
        if lib.sfcgal_geometry_is_measured(self._geom):
            return lib.sfcgal_point_m(self._geom)
        else:
            raise DimensionError("This point has no m coordinate.")

    @cond_icontract(
        lambda self, radius, segments: (
            self.is_valid() and radius > 0 and segments > 3
        ),
        "require",
    )
    def buffer_3d(self, radius: float, segments: int) -> Optional[Geometry]:
        """
        Computes a 3D buffer around a Point

        Parameters
        ----------
        radius : float
            The buffer radius
        segments : int
            The number of segments to use for approximating curved surfaces

        Returns
        -------
        Geometry
            The buffered geometry

        """
        geom = lib.sfcgal_geometry_buffer3d(self._geom, radius, segments, 0)
        return Geometry.from_sfcgal_geometry(geom)

    def to_coordinates(self) -> Tuple[Coord, ...]:
        """Generates the coordinates of the Point.

        Returns
        -------
        tuple
            Two, three or four floating points depending on the point nature.
        """
        coords: Tuple[Point.Coord, ...] = (self.x, self.y)
        if self.has_m:
            coords += (self.z if self.has_z else math.nan, self.m)
        elif self.has_z:
            coords = (*coords, self.z)
        return coords

    @property
    def coords(self) -> Tuple[Coord, ...]:
        """Propery alias for to_coordinates."""
        return self.to_coordinates()

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Point:
        """Instantiates a Point starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Point coordinates.

        Returns
        -------
        Point
            The Point that corresponds to the provided coordinates

        """
        return cls(*coordinates)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Point starting from a list of coordinates.
        If the coordinates are None or if the list is empty, an empty point is returned.

        Parameters
        ----------
        coordinates : list
            Point coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        length_coordinates = len(coordinates)
        if length_coordinates == 0:
            return lib.sfcgal_point_create()
        elif length_coordinates < 2 or length_coordinates > 4:
            raise DimensionError("Coordinates length must be 2, 3 or 4.")

        if all(coord is None for coord in coordinates):
            return lib.sfcgal_point_create()
        elif any(coord is None for coord in coordinates[:2]):
            raise ValueError(
                f"These coordinate set is unvalid ({coordinates}), "
                "X and Y must be defined."
            )

        if length_coordinates == 2:
            return lib.sfcgal_point_create_from_xy(*coordinates)
        elif length_coordinates == 3:
            return lib.sfcgal_point_create_from_xyz(*coordinates)
        elif length_coordinates == 4:
            has_z = coordinates[2] is not None
            has_m = coordinates[3] is not None
            if not has_z and not has_m:
                return lib.sfcgal_point_create_from_xy(coordinates[0], coordinates[1])
            elif has_z and not has_m:
                return lib.sfcgal_point_create_from_xyz(
                    coordinates[0], coordinates[1], coordinates[2]
                )
            elif not has_z and has_m:
                return lib.sfcgal_point_create_from_xym(
                    coordinates[0], coordinates[1], coordinates[3]
                )
            else:
                return lib.sfcgal_point_create_from_xyzm(*coordinates)
