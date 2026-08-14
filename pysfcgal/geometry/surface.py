"""Simple Feature surface geometries.

One denotes Polygon, Triangle, PolyhedralSurface and Tin.

As a side note, PolyhedralSurface is strongly related to Solid, which is defined in
`volume.py` (PolyhedralSurface represents the shells of Solid, as LineString models the
rings of Polygon).

"""


from __future__ import annotations

import typing
from typing import cast

if typing.TYPE_CHECKING:
    from .collection import MultiPolygon
    from .volume import Solid
from .._contracts import cond_icontract
from .._sfcgal import ffi, lib
from .curve import LineString, is_segment_in_coordsequence
from .geometry import Geometry
from .point import Point

__all__ = [
    "Polygon",
    "PolyhedralSurface",
    "Tin",
    "Triangle",
]


class Polygon(Geometry):
    """Polygon

    Attributes
    ----------
    _geom : _cffi_backend._CDatabase
        SFCGAL polygon associated to the Polygon instance. The operations on the
        geometry are done at the SFCGAL lower level.
    """

    def __init__(self, exterior: tuple = (), interiors: tuple | None = None):
        """Initialize a Polygon with given exterior and optional interior rings.

        Parameters
        ----------
        exterior : tuples of tuples
            A list of coordinates defining the exterior ring of the polygon.
        interiors : tuple of tuple of tuples, optional
            A list of interior rings, where each interior is defined by a list of
            coordinates. Default is None, which initializes to an empty list.
        """
        if interiors is None:
            interiors = ()
        self._geom = self.sfcgal_geom_from_coordinates(
            [
                exterior,
                *interiors,
            ]
        )

    def __iter__(self):
        """Iterate over the rings of the Polygon.

        Yields
        ------
        Geometry
            The exterior and interior rings of the Polygon.
        """
        for n in range(1 + self.n_interiors):
            yield self.__get_ring_n(n)

    def __getitem__(self, key):
        """Get a ring (or several) within a polygon, identified through an index or a
        slice. The first ring is always the exterior ring, the next ones are the
        interior rings (optional).

        Raises an IndexError if the key is unvalid for the geometry.

        Raises a TypeError if the key is neither an integer or a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the ring(s) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The specified ring or a list of rings if a slice is provided.
        """
        length = 1 + self.n_interiors
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_ring_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_ring_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Two Polygons are equal if their rings (exterior and interior) are equal.

        Parameters
        ----------
        other : Polygon
            The Polygon to compare against.

        Returns
        -------
        bool
            True if the Polygons are equal, False otherwise.
        """
        if not isinstance(other, Polygon):
            return False
        if self.exterior != other.exterior:
            return False
        if self.n_interiors != other.n_interiors:
            return False
        for p, other_p in zip(self.interiors, other.interiors):
            if p != other_p:
                return False
        return True

    @property
    def exterior(self):
        """Get the exterior ring of the Polygon.

        Returns
        -------
        Geometry
            The exterior ring of the Polygon.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_polygon_exterior_ring(self._geom), owned=False, parent=self,
        )

    @cond_icontract(
        lambda self, ring: ring.geom_type == "LineString", "require")
    def set_exterior_ring(self, ring: LineString) -> None:
        """Sets the exterior ring of the polygon.

        Parameters
        ----------
        ring : LineString
            The new exterior ring

        """
        ring_clone = lib.sfcgal_geometry_clone(ring._geom)
        lib.sfcgal_polygon_set_exterior_ring(self._geom, ring_clone)

    @property
    def n_interiors(self):
        """Get the number of interior rings in the Polygon.

        Returns
        -------
        int
            The number of interior rings.
        """
        return lib.sfcgal_polygon_num_interior_rings(self._geom)

    @property
    def interiors(self):
        """Get a list of the interior rings of the Polygon.

        Returns
        -------
        list of Geometry
            A list of interior rings.
        """
        interior_rings = []
        for idx in range(self.n_interiors):
            interior_rings.append(
                Geometry.from_sfcgal_geometry(
                    lib.sfcgal_polygon_interior_ring_n(self._geom, idx), owned=False,
                    parent=self
                )
            )
        return interior_rings

    @cond_icontract(
        lambda self, ring: ring.geom_type == "LineString", "require")
    def add_interior_ring(self, ring: LineString) -> None:
        """Adds an interior ring to the polygon.

        Parameters
        ----------
        ring : LineString
            The interior ring to add

        """
        ring_clone = lib.sfcgal_geometry_clone(ring._geom)
        lib.sfcgal_polygon_add_interior_ring(self._geom, ring_clone)

    @property
    def rings(self):
        """Get all the rings of the Polygon, including the exterior and interior rings.

        Returns
        -------
        list of Geometry
            A list containing the exterior ring followed by the interior rings.
        """
        return [self.exterior] + self.interiors

    def __get_ring_n(self, n):
        """Returns the n-th ring within a polygon. This method is internal and makes the
        assumption that the index is valid for the geometry. The 0 index refers to the
        exterior ring.

        Parameters
        ----------
        n : int
            Index of the ring to recover.

        Returns
        -------
        Geometry
            The ring at the specified index.
        """
        return self.rings[n]

    def has_exterior_edge(self, point_a: Point, point_b: Point) -> bool:
        """Check if the polygon has an edge defined by the two given points.

        This method verifies whether the line segment between point_a and point_b lies
        within the exterior ring of the polygon.

        Parameters
        ----------
        point_a : Point
            The first point defining the edge.
        point_b : Point
            The second point defining the edge.

        Returns
        -------
        bool
            True if the edge is part of the exterior ring, False otherwise.
        """
        poly_coordinates = self.to_coordinates()
        exterior_coordinates = poly_coordinates[0]
        return is_segment_in_coordsequence(exterior_coordinates, point_a, point_b)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the Polygon.

        Returns
        -------
        list
            List of the polygon ring coordinates
        """
        return [ring.to_coordinates() for ring in self.rings]

    def _validate_ring_values(
        self,
        values: list[list[float]],
        label: str,
    ) -> tuple[list[float], list[int], int]:
        """Validate per-ring per-edge values and return their flattened form.

        Parameters
        ----------
        values : list of list of float
            One inner list per ring (exterior first, then holes).
        label : str
            Human-readable name used in error messages (e.g. ``"angles"``).

        Returns
        -------
        tuple
            ``(flattened, per_ring, num_rings)`` ready for CFFI array creation.

        Raises
        ------
        TypeError
            If *values* is ``None``.
        ValueError
            If the number of inner lists does not match the ring count, or if
            an inner list length does not match the edge count of that ring.
        """
        if values is None:
            raise TypeError(f"'{label}' must be provided")
        num_rings = 1 + self.n_interiors
        if len(values) != num_rings:
            raise ValueError(
                f"Expected {num_rings} rings of {label}, but got {len(values)}"
            )
        flattened = []
        per_ring = []
        for i, ring_values in enumerate(values):
            coords = self.rings[i].to_coordinates()
            if len(coords) == 0:
                raise ValueError(f"Ring {i} is empty; cannot validate {label}")
            # A closed ring has first == last point; edges = points - 1.
            num_edges = len(coords) - 1 if coords[0] == coords[-1] else len(coords)
            if len(ring_values) != num_edges:
                raise ValueError(
                    f"Ring {i} has {num_edges} edges, "
                    f"but {len(ring_values)} {label} were provided"
                )
            flattened.extend(ring_values)
            per_ring.append(len(ring_values))
        return flattened, per_ring, num_rings

    @cond_icontract(
        lambda self, height: self.is_valid() and height != 0,
        "require",
    )
    def extrude_straight_skeleton(self, height: float) -> PolyhedralSurface | None:
        """Extrude the polygon along its straight skeleton.

        Parameters
        ----------
        height : float
            The extrusion height. Must be non-zero.

        Returns
        -------
        PolyhedralSurface or None
            The resulting extruded geometry, or ``None`` if SFCGAL returns NULL.
        """
        geom = lib.sfcgal_geometry_extrude_straight_skeleton(self._geom, height)
        return cast(PolyhedralSurface | None, Geometry.from_sfcgal_geometry(geom))

    @cond_icontract(
        lambda self, building_height, roof_height: self.is_valid() and roof_height != 0,
        "require",
    )
    def extrude_polygon_straight_skeleton(
        self, building_height: float, roof_height: float
    ) -> PolyhedralSurface | None:
        """Extrude the polygon along its straight skeleton with building
        and roof heights.

        Parameters
        ----------
        building_height : float
            The height of the building walls.
        roof_height : float
            The height of the roof. Must be non-zero.

        Returns
        -------
        PolyhedralSurface or None
            The union of the wall extrusion and the roof extrusion, or ``None``
            if SFCGAL returns NULL.
        """
        geom = lib.sfcgal_geometry_extrude_polygon_straight_skeleton(
            self._geom, building_height, roof_height
        )
        return cast(PolyhedralSurface | None, Geometry.from_sfcgal_geometry(geom))

    @cond_icontract(
        lambda self, height, angles: self.is_valid() and height != 0,
        "require",
    )
    def extrude_straight_skeleton_with_angles(
        self,
        height: float,
        angles: list[list[float]],
    ) -> PolyhedralSurface | None:
        """Extrude the polygon along its straight skeleton using per-edge angles.

        Parameters
        ----------
        height : float
            The extrusion height. Must be non-zero.
        angles : list of list of float
            Angles in degrees for each edge of each ring (exterior first, then
            holes).  The C library requires ``0 < angle < 180`` for every value.

        Returns
        -------
        PolyhedralSurface or None
            The resulting extruded geometry, or ``None`` if SFCGAL returns NULL.
        """
        flattened, per_ring, num_rings = self._validate_ring_values(angles, "angles")
        c_angles = ffi.new("double[]", flattened)
        c_per_ring = ffi.new("size_t[]", per_ring)
        result_geom = lib.sfcgal_geometry_extrude_straight_skeleton_with_angles(
            self._geom, height, c_angles, c_per_ring, num_rings
        )
        geom = Geometry.from_sfcgal_geometry(result_geom)
        return cast(PolyhedralSurface | None, geom)

    @cond_icontract(
        lambda self, building_height, roof_height, angles: (
            self.is_valid() and roof_height != 0
        ),
        "require",
    )
    def extrude_polygon_straight_skeleton_with_angles(
        self,
        building_height: float,
        roof_height: float,
        angles: list[list[float]],
    ) -> PolyhedralSurface | None:
        """Extrude the polygon with a straight-skeleton roof and per-edge angles.

        Produces the union of the vertical wall extrusion (up to *building_height*)
        and the angled roof extrusion (up to *roof_height*).

        Parameters
        ----------
        building_height : float
            The height of the building walls.
        roof_height : float
            The maximum height of the roof. Must be non-zero.
        angles : list of list of float
            Angles in degrees for each edge of each ring.  Requires
            ``0 < angle < 180`` for every value.

        Returns
        -------
        PolyhedralSurface or None
            The resulting geometry, or ``None`` if SFCGAL returns NULL.
        """
        flattened, per_ring, num_rings = self._validate_ring_values(angles, "angles")
        c_angles = ffi.new("double[]", flattened)
        c_per_ring = ffi.new("size_t[]", per_ring)
        result_geom = lib.sfcgal_geometry_extrude_polygon_straight_skeleton_with_angles(
            self._geom, building_height, roof_height, c_angles, c_per_ring, num_rings
        )
        geom = Geometry.from_sfcgal_geometry(result_geom)
        return cast(PolyhedralSurface | None, geom)

    @cond_icontract(
        lambda self, height, weights: self.is_valid() and height != 0,
        "require",
    )
    def extrude_straight_skeleton_with_weights(
        self,
        height: float,
        weights: list[list[float]],
    ) -> PolyhedralSurface | None:
        """Extrude the polygon along its straight skeleton using per-edge weights.

        Weights are the tangent of the desired roof-face angle (``tan(angle)``).

        Parameters
        ----------
        height : float
            The extrusion height. Must be non-zero.
        weights : list of list of float
            Weights for each edge of each ring (exterior first, then holes).

        Returns
        -------
        PolyhedralSurface or None
            The resulting extruded geometry, or ``None`` if SFCGAL returns NULL.
        """
        flattened, per_ring, num_rings = self._validate_ring_values(weights, "weights")
        c_weights = ffi.new("double[]", flattened)
        c_per_ring = ffi.new("size_t[]", per_ring)
        result_geom = lib.sfcgal_geometry_extrude_straight_skeleton_with_weights(
            self._geom, height, c_weights, c_per_ring, num_rings
        )
        geom = Geometry.from_sfcgal_geometry(result_geom)
        return cast(PolyhedralSurface | None, geom)

    @cond_icontract(
        lambda self, building_height, roof_height, weights: (
            self.is_valid() and roof_height != 0
        ),
        "require",
    )
    def extrude_polygon_straight_skeleton_with_weights(
        self,
        building_height: float,
        roof_height: float,
        weights: list[list[float]],
    ) -> PolyhedralSurface | None:
        """Extrude the polygon with a straight-skeleton roof and per-edge weights.

        Produces the union of the vertical wall extrusion (up to *building_height*)
        and the weighted roof extrusion (up to *roof_height*).

        Parameters
        ----------
        building_height : float
            The height of the building walls.
        roof_height : float
            The maximum height of the roof. Must be non-zero.
        weights : list of list of float
            Weights for each edge of each ring.

        Returns
        -------
        PolyhedralSurface or None
            The resulting geometry, or ``None`` if SFCGAL returns NULL.
        """
        flattened, per_ring, num_rings = self._validate_ring_values(weights, "weights")
        c_weights = ffi.new("double[]", flattened)
        c_per_ring = ffi.new("size_t[]", per_ring)
        result_geom = (
            lib.sfcgal_geometry_extrude_polygon_straight_skeleton_with_weights(
                self._geom, building_height, roof_height,
                c_weights, c_per_ring, num_rings
            )
        )
        geom = Geometry.from_sfcgal_geometry(result_geom)
        return cast(PolyhedralSurface | None, geom)

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Polygon | None:
        """Instantiates a Polygon starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Polygon coordinates. The first item corresponds to the coordinates of the
            exterior ring, whilst the following items are the coordinates of the
            interior rings, if they exist.

        Returns
        -------
        Polygon
            The Polygon that corresponds to the provided coordinates

        """
        return cls(
            tuple(coordinates[0]),
            tuple(coordinates[1:]) if len(coordinates) > 0 else None,
        )

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Polygon starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Polygon coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Polygon

        """
        if len(coordinates) == 0 or len(coordinates[0]) == 0:
            return lib.sfcgal_polygon_create()
        exterior = LineString.sfcgal_geom_from_coordinates(coordinates[0], True)
        polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
        for n in range(1, len(coordinates)):
            interior = LineString.sfcgal_geom_from_coordinates(coordinates[n], True)
            lib.sfcgal_polygon_add_interior_ring(polygon, interior)
        return polygon


class Tin(Geometry):
    def __init__(self, coords: tuple = ()):
        """Initialize the Tin with a tuple of coordinates.

        Parameters
        ----------
        coords : tuple
            A list of coordinate tuples that define the vertices of the TIN.
            If None, initializes an empty TIN.
        """
        self._geom = Tin.sfcgal_geom_from_coordinates(list(coords))

    def __len__(self):
        """Return the number of patches in the TIN.

        Returns
        -------
        int
            The number of patches that comprise the TIN.
        """
        return lib.sfcgal_triangulated_surface_num_patches(self._geom)

    def __iter__(self):
        """Iterate over the patches in the TIN.

        Yields
        ------
        Geometry
            Each patch in the TIN as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_triangulated_surface_patch_n(self._geom, n),
                owned=False, parent=self,
            )

    def __get_geometry_n(self, n: int) -> Polygon | None:
        """Returns the n-th patch within the TIN.

        This method assumes that the index is valid for the TIN.

        Parameters
        ----------
        n : int
            Index of the triangle to recover.

        Returns
        -------
        Geometry
            The patch at the specified index as a Geometry object.
        """
        return cast(Polygon, Geometry.from_sfcgal_geometry(
            lib.sfcgal_triangulated_surface_patch_n(self._geom, n),
            owned=False, parent=self
        ))

    def __getitem__(self, key):
        """Get a patch (or several) within the TIN, identified through an index or a
        slice.

        Raises an IndexError if the key is invalid for the TIN.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the patch(es) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The patch(es) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    @cond_icontract(lambda self, n: n >= 0 and n < len(self), "require")
    @cond_icontract(lambda self, patch: patch.geom_type == "Triangle", "require")
    def set_patch_n(self, patch: Triangle, n: int) -> None:
        """Set the n-th patch of the Tin.

        Parameters
        ----------
        patch: Triangle
            Geometry that will be set at the i-th position in the Tin
        n: int
            Index of the triangle to overwrite.
        """
        clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_triangulated_surface_set_patch_n(self._geom, clone, n)

    def __eq__(self, other: object) -> bool:
        """Check if two TINs are equal based on their patches.

        Parameters
        ----------
        other : Tin
            The other TIN to compare.

        Returns
        -------
        bool
            True if both TINs contain the same patches, False otherwise.
        """
        if not isinstance(other, Tin):
            return False
        return self[:] == other[:]

    def to_multipolygon(self, wrapped: bool = True) -> MultiPolygon | ffi.CData:
        """Convert the TIN to a MultiPolygon.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the result in a Geometry object. Defaults to True.

        Returns
        -------
        MultiPolygon
            A MultiPolygon representation of the TIN.
        """
        multipolygon = lib.sfcgal_multi_polygon_create()
        num_geoms = lib.sfcgal_triangulated_surface_num_patches(self._geom)
        for geom_idx in range(num_geoms):
            triangle_geom = lib.sfcgal_triangulated_surface_patch_n(
                self._geom, geom_idx
            )
            triangle_clone = lib.sfcgal_geometry_clone(triangle_geom)
            triangle_clone_wrap = cast(
                Triangle, Geometry.from_sfcgal_geometry(triangle_clone))
            polygon = triangle_clone_wrap.to_polygon(wrapped=False)
            lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
        return Geometry.from_sfcgal_geometry(multipolygon) if wrapped else multipolygon

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Tin starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Tin coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Tin

        """
        tin = lib.sfcgal_triangulated_surface_create()
        for coords in coordinates:
            triangle = Triangle.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_triangulated_surface_add_patch(tin, triangle)
        return tin

    @cond_icontract(lambda self, patch: patch.geom_type == "Triangle", "require")
    def add_patch(self, patch: Triangle) -> None:
        """Add a triangle to the Tin.

        Parameters
        ----------
        patch: Triangle
            The patch to add.
        """
        patch_clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_triangulated_surface_add_patch(self._geom, patch_clone)

    @property
    def n_edges(self) -> int:
        """Get the number of edges in the TIN.

        Two adjacent triangles are connected through an edge.

        Returns
        -------
        int
            Number of edges.
        """
        return lib.sfcgal_triangulated_surface_num_edges(self._geom)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the TIN

        Uses the __iter__ property of the TIN to iterate over patches.

        Returns
        -------
        list
            List of patches' coordinates.
        """
        return [patch.to_coordinates() for patch in self]


class Triangle(Geometry):
    def __init__(self, coords=None):
        """Initialize the Triangle with the given coordinates.

        If the coordinates sequence does not contain three items, an empty Triangle is
        returned.

        Parameters
        ----------
        coords : list of tuples, optional
            A list of coordinate tuples that define the vertices of the triangle.
            If None, initializes an empty triangle.

        """
        self._geom = Triangle.sfcgal_geom_from_coordinates(coords)

    @property
    def coords(self):
        """Get the coordinates of the triangle.

        Returns
        -------
        list of tuples
            The coordinates of the triangle's vertices.
        """
        return self.to_coordinates()

    def __iter__(self):
        """Iterate over the vertices of the triangle.

        Yields
        ------
        Geometry
            Each vertex of the triangle as a Geometry object.
        """
        for n in range(3):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_triangle_vertex(self._geom, n),
                owned=False, parent=self,
            )

    def __get_geometry_n(self, n: int) -> Point | None:
        """Returns the n-th vertex of the triangle.

        This method assumes that the index is valid for the triangle.

        Parameters
        ----------
        n : int
            Index of the vertex to recover.

        Returns
        -------
        Geometry
            The vertex at the specified index as a Geometry object.
        """
        return cast(Point, Geometry.from_sfcgal_geometry(
            lib.sfcgal_triangle_vertex(self._geom, n),
            owned=False, parent=self,
        ))

    def __getitem__(self, key):
        """Get a vertex (or several) within the triangle, identified through an index
        or a slice.

        Raises an IndexError if the key is invalid for the triangle.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the vertex(es) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The vertex(es) at the specified index or slice.
        """
        length = 3
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Check if two triangles are equal based on their vertices.

        Parameters
        ----------
        other : Triangle
            The other triangle to compare.

        Returns
        -------
        bool
            True if both triangles contain the same vertices, False otherwise.
        """
        if not isinstance(other, Triangle):
            return False
        return all(vertex == other_vertex for vertex, other_vertex in zip(self, other))

    def to_polygon(self, wrapped: bool = True) -> Polygon | ffi.CData:
        """Convert the triangle to a Polygon.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the result in a Geometry object. Defaults to True.

        Returns
        -------
        Polygon
            A Polygon representation of the triangle.
        """
        exterior = lib.sfcgal_linestring_create()
        for point_idx in range(4):
            point = lib.sfcgal_triangle_vertex(self._geom, point_idx)
            lib.sfcgal_linestring_add_point(exterior, lib.sfcgal_geometry_clone(point))
        polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
        return Geometry.from_sfcgal_geometry(polygon) if wrapped else polygon

    def to_coordinates(self):
        """Generates the coordinates of the Triangle.

        Uses the __iter__ property of the Triangle to iterate over vertices.

        Returns
        -------
        list
            List of the vertex coordinates
        """
        return [vertex.to_coordinates() for vertex in self]

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Triangle starting from a list of coordinates.

        If the coordinates sequence does not contain three items, an empty Triangle is
        returned

        Parameters
        ----------
        coordinates : list
            Triangle coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Triangle

        """
        triangle = None
        if coordinates and len(coordinates) == 3:
            triangle = lib.sfcgal_triangle_create_from_points(
                Point.sfcgal_geom_from_coordinates(coordinates[0]),
                Point.sfcgal_geom_from_coordinates(coordinates[1]),
                Point.sfcgal_geom_from_coordinates(coordinates[2]),
            )
        else:
            triangle = lib.sfcgal_triangle_create()

        return triangle


class PolyhedralSurface(Geometry):
    def __init__(self, coords: tuple = ()):
        """Initialize the PolyhedralSurface with a tuple of coordinates.

        Parameters
        ----------
        coords : tuple
            A tuple of coordinates that define the patches of the polyhedral
            surface. If empty, initializes an empty polyhedral surface.
        """
        self._geom = PolyhedralSurface.sfcgal_geom_from_coordinates(list(coords))

    def __len__(self):
        """Get the number of patches in the polyhedral surface.

        Returns
        -------
        int
            The number of patches contained within the polyhedral surface.
        """
        return lib.sfcgal_polyhedral_surface_num_patches(self._geom)

    def __iter__(self):
        """Iterate over the patches of the polyhedral surface.

        Yields
        ------
        Geometry
            Each patch of the polyhedral surface as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_polyhedral_surface_patch_n(self._geom, n),
                owned=False, parent=self,
            )

    def __get_geometry_n(self, n: int) -> Polygon | None:
        """Returns the n-th polygon within the polyhedral surface.

        This method assumes that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the polygon to recover.

        Returns
        -------
        Geometry
            The polygon at the specified index as a Geometry object.
        """
        return cast(Polygon, Geometry.from_sfcgal_geometry(
            lib.sfcgal_polyhedral_surface_patch_n(self._geom, n),
            owned=False, parent=self,
        ))

    def __getitem__(self, key):
        """Get a patch (or several) within the polyhedral surface, identified through
        an index or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the polygon(s) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The patch(es) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    @cond_icontract(lambda self, n: n >= 0 and n < len(self), "require")
    @cond_icontract(lambda self, patch: patch.geom_type == "Polygon", "require")
    def set_patch_n(self, patch: Polygon, n: int) -> None:
        """Set the n-th patch of the PolyhedralSurface.

        Parameters
        ----------
        patch: Polygon
            Geometry that will be set at the i-th position in the PolyhedralSurface
        n: int
            Index of the polygon to overwrite.
        """
        clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_polyhedral_surface_set_patch_n(self._geom, clone, n)

    def __eq__(self, other: object) -> bool:
        """Check if two polyhedral surfaces are equal based on their patches.

        Parameters
        ----------
        other : PolyhedralSurface
            The other polyhedral surface to compare.

        Returns
        -------
        bool
            True if both polyhedral surfaces contain the same polygons, False otherwise.
        """
        if not isinstance(other, PolyhedralSurface):
            return False
        return self[:] == other[:]

    @property
    def n_edges(self) -> int:
        """Get the number of edges in the polyhedron.

        Two adjacent polygons are connected through an edge.

        Returns
        -------
        int
            Number of edges.
        """
        return lib.sfcgal_polyhedral_surface_num_edges(self._geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def to_multipolygon(self, wrapped: bool = True) -> MultiPolygon | ffi.CData:
        """Convert the polyhedralsurface to a MultiPolygon.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the result in a Geometry object. Defaults to True.

        Returns
        -------
        MultiPolygon
            A MultiPolygon representation of the PolyhedralSurface.
        """
        multipolygon = lib.sfcgal_multi_polygon_create()
        num_geoms = lib.sfcgal_polyhedral_surface_num_patches(self._geom)
        for geom_idx in range(num_geoms):
            polygon_geom = lib.sfcgal_polyhedral_surface_patch_n(
                self._geom, geom_idx
            )
            polygon_clone = lib.sfcgal_geometry_clone(polygon_geom)
            lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon_clone)
        return Geometry.from_sfcgal_geometry(multipolygon) if wrapped else multipolygon

    @cond_icontract(lambda self: self.is_valid(), "require")
    def to_solid(self) -> Solid:
        """Convert the polyhedralsurface into a solid.

        Returns
        -------
        Solid
            A solid version of the polyhedralsurface.
        """
        from .volume import Solid

        geom = lib.sfcgal_geometry_make_solid(self._geom)
        return cast(Solid, PolyhedralSurface.from_sfcgal_geometry(geom))

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL PolyhedralSurface starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            PolyhedralSurface coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL PolyhedralSurface

        """
        polyhedralsurface = lib.sfcgal_polyhedral_surface_create()
        for coords in coordinates:
            polygon = Polygon.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_polyhedral_surface_add_patch(polyhedralsurface, polygon)
        return polyhedralsurface

    @cond_icontract(lambda self, patch: patch.geom_type == "Polygon", "require")
    def add_patch(self, patch: Polygon) -> None:
        """Add a patch to the polyhedralsurface.

        Parameters
        ----------
        patch: Polygon
            The patch to add.
        """
        patch_clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_polyhedral_surface_add_patch(self._geom, patch_clone)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the PolyhedralSurface.

        Uses the __iter__ property of the PolyhedralSurface to iterate over patches.

        Returns
        -------
        list
            List of patches' coordinates.
        """
        return [patch.to_coordinates() for patch in self]
