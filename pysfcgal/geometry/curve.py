"""Simple Feature curve geometries (LineString)."""


from __future__ import annotations

from typing import Tuple

from .._contracts import cond_icontract
from .._sfcgal import ffi, lib
from .buffer import BufferType
from .geometry import Geometry
from .point import Point

__all__ = ["CoordinateSequence", "LineString"]


def is_segment_in_coordsequence(coords: list, point_a: Point, point_b: Point) -> bool:
    """Check if the segment defined by two points is in the coordinate sequence.

    Parameters
    ----------
    coords : list
        A list of coordinate tuples.
    point_a : Point
        The first point defining the segment.
    point_b : Point
        The second point defining the segment.

    Returns
    -------
    bool
        True if the segment is found in the coordinate sequence, False otherwise.
    """
    for c1, c2 in zip(coords[1:], coords[:-1]):
        # (point_a, point_b) is in the coord sequence
        if c1 == (point_a.x, point_a.y) and c2 == (point_b.x, point_b.y):
            return True
        # (point_a, point_b) is in reverted coord sequence
        if c2 == (point_a.x, point_a.y) and c1 == (point_b.x, point_b.y):
            return True
    return False


class CoordinateSequence:
    def __init__(self, parent):
        """Initialize the CoordinateSequence with a parent geometry.

        Parameters
        ----------
        parent : Geometry
            The parent geometry object that this sequence is associated with.
        """
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __len__(self):
        """Return the number of coordinates in the sequence.

        Returns
        -------
        int
            The number of coordinates in the sequence.
        """
        return self._parent.__len__()

    def __iter__(self):
        """Iterate over the coordinates in the sequence.

        Yields
        ------
        tuple
            A tuple representing the coordinates of each point.
        """
        length = self.__len__()
        for n in range(0, length):
            yield self.__get_coord_n(n)

    def __get_coord_n(self, n):
        """Returns the n-th coordinate within the sequence.

        This method makes the assumption that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the coordinate to recover.

        Returns
        -------
        tuple
            A tuple representing the coordinates of the point at index n.
        """
        point_n = lib.sfcgal_linestring_point_n(self._parent._geom, n)
        return Point.from_sfcgal_geometry(point_n, owned=False).to_coordinates()

    def __getitem__(self, key):
        """Get a coordinate (or several) within the sequence, identified through an
        index or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the coordinate(s) to recover.

        Returns
        -------
        tuple or list of tuples
            The coordinate(s) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_coord_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_coord_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )


class LineString(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize a LineString with a tuple of point coordinates.

        Parameters
        ----------
        coords : list of tuples
            A list of tuples where each tuple represents the coordinates of a point in
            the LineString.
        """
        self._geom = self.sfcgal_geom_from_coordinates(list(coords))

    def __eq__(self, other: object) -> bool:
        """Two LineStrings are equals if they contain the same points in the same
        order."""
        if not isinstance(other, LineString):
            return False
        if len(self) != len(other):
            return False
        for p, other_p in zip(self, other):
            if not p == other_p:
                return False
        return True

    def __len__(self):
        """Return the number of points in the LineString.

        Returns
        -------
        int
            The number of points in the LineString.
        """
        return lib.sfcgal_linestring_num_points(self._geom)

    def __iter__(self):
        """Iterate over the points in the LineString.

        Yields
        ------
        Point
            The points in the LineString.
        """
        for n in range(len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_linestring_point_n(self._geom, n),
                owned=False, parent=self,
            )

    def __get_point_n(self, n):
        """Returns the n-th point within a linestring. This method is internal and makes
        the assumption that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the point to recover.

        Returns
        -------
        Point
            Point at the index n.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_linestring_point_n(self._geom, n), owned=False, parent=self,
        )

    def __getitem__(self, key):
        """Get a point (or several) within a linestring, identified through an index or
        a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer or a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the point(s) to recover.

        Returns
        -------
        Point or list of Points
            The Point(s) at the specified index or indices.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_point_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_point_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    @property
    def coords(self):
        """Return the coordinates of the LineString as a CoordinateSequence.

        Returns
        -------
        CoordinateSequence
            A sequence of coordinates representing the points in the LineString.
        """
        return CoordinateSequence(self)

    def has_edge(self, point_a: Point, point_b: Point) -> bool:
        """Check if the LineString contains the edge between two points.

        Parameters
        ----------
        point_a : Point
            The first point of the edge.
        point_b : Point
            The second point of the edge.

        Returns
        -------
        bool
            True if the edge exists in the LineString, False otherwise.
        """
        return is_segment_in_coordsequence(self.to_coordinates(), point_a, point_b)

    @cond_icontract(
        lambda self, radius, segments, buffer_type: (
            self.is_valid() and radius > 0 and segments > 3 and (
                isinstance(buffer_type, BufferType)
                or (isinstance(buffer_type, int) and buffer_type in (0, 1, 2))
            )
        ),
        "require",
    )
    def buffer_3d(
        self, radius: float, segments: int, buffer_type: BufferType | int
    ) -> Geometry | None:
        """
        Computes a 3D buffer around a LineString

        Parameters
        ----------
        radius : float
            The buffer radius
        segments : int
            The number of segments to use for approximating curved surfaces
        buffer_type : BufferType|int
            Either 0 (SFCGAL_BUFFER3D_ROUND, Minkowski sum with a sphere),
            1 (SFCGAL_BUFFER3D_CYLSPHERE: Union of cylinders and spheres) or
            2 (SFCGAL_BUFFER3D_FLAT: Construction of a disk on the bisector plane)

        Returns
        -------
        Geometry
            The buffered geometry

        """
        if isinstance(buffer_type, BufferType):
            buffer_type = buffer_type.value
        geom = lib.sfcgal_geometry_buffer3d(self._geom, radius, segments, buffer_type)
        return Geometry.from_sfcgal_geometry(geom)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the LineString.

        Uses the __iter__ property of the LineString to iterate over points.

        Returns
        -------
        list
            List of point coordinates.
        """
        return [point.to_coordinates() for point in self]

    def add_point(self, point: Point) -> None:
        """Appends a point to the end of the LineString

        Parameters
        ----------
        point : Point
            Point to append to the LineString
        """
        point_clone = lib.sfcgal_geometry_clone(point._geom)
        lib.sfcgal_linestring_add_point(self._geom, point_clone)

    def close(self) -> None:
        """Closes the line string if it is not already closed.

        This is achieved by appending the first point to the end of the
        line.
        """
        lib.sfcgal_linestring_closes(self._geom)

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: list, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL LineString starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            LineString coordinates.
        close : bool
            If True, the LineString is built as closed even if the coordinates are not,
            i.e. the first point is replicated at the last position.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL LineString

        """
        linestring = lib.sfcgal_linestring_create()
        for coordinate in coordinates:
            cpoint = Point.sfcgal_geom_from_coordinates(coordinate)
            lib.sfcgal_linestring_add_point(linestring, cpoint)
        if close and coordinates[0] != coordinates[-1]:
            cpoint = Point.sfcgal_geom_from_coordinates(coordinates[0])
            lib.sfcgal_linestring_add_point(linestring, cpoint)
        return linestring
