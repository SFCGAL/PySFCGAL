"""The `sfcgal` module is the main module of PySFCGAL.

It contains the definition of every geometry classes, plus some I/O functions.
"""

from __future__ import annotations

import platform
import typing
from typing import Optional, Tuple, Union, cast

if typing.TYPE_CHECKING:
    from .vector import Vector3D
    from .collection import GeometryCollection
    from .point import Point

from .._contracts import cond_icontract
from .._deprecated import deprecated
from .._sfcgal import ffi, lib
from ..vector import UNIT_X, UNIT_Y, UNIT_Z
from .simplification import SimplificationStrategy

__all__ = ["Geometry"]


# Required until Alpha Shapes bug is not fixed on MSVC
compiler = platform.python_compiler()


class Geometry:
    """Geometry mother class, from which every other geometry class inheritates.

    It defines a large bunch of methods that are shared along every geometries.

    Attributes
    ----------
    _owned : bool, default True
        If True, the Python geometry owns the low-level SFCGAL geometry, which is
        removed when the Python structure is cleaned by the garbage collector.

    _geom : _cffi_backend._CDatabase
        SFCGAL geometry associated to the Python Geometry. The operations on the
        geometry are done at the SFCGAL lower level.

    _parent : Optional[Geometry], default None
        Optional parent Geometry that this geometry depends on.
        This ensures that the parent geometry is not garbage collected by the Python
        interpreter while it is still in use.
        For example, a point extracted from a linestring.

    """
    _geom: ffi.CData
    _owned = True
    _parent: Optional[Geometry] = None

    @property
    def validity_flag(self) -> bool:
        """Returns whether the geometry has a validity flag.

        The validity flag indicates that the geometry is assumed to be valid, skipping
        any validity check. Setting this flag may improve the performance of PySFCGAL
        operations, as validity checks can be time-consuming.

        Returns
        -------
        bool
            Geometry validity flag.

        """
        return bool(lib.sfcgal_geometry_has_validity_flag(self._geom))

    @validity_flag.setter
    def validity_flag(self, flag: bool) -> None:
        """Set the geometry validity flag.

        By forcing the validity flag to True, validity checks will be skipped entirely.
        Otherwise if the flag is forced to False, the geometry validity is not
        guaranteed, a validity check will have to be done as soon as another method
        requires it (either explicitely through the is_valid() method or internally on
        the SFCGAL-side).

        The flag is set according to the validity status when is_valid() is called.

        Parameters
        ----------
        flag: bool
            Validity flag that has to be set for the current geometry.

        """
        lib.sfcgal_geometry_force_valid(self._geom, flag)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def distance(self, other: Geometry) -> float:
        """
        Compute the 2D Euclidean distance between this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry object to compute the distance to.

        Returns
        -------
        float
            The 2D Euclidean distance between the two geometries.
        """
        return lib.sfcgal_geometry_distance(self._geom, other._geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def distance_3d(self, other: Geometry) -> float:
        """
        Compute the 3D Euclidean distance between this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry object to compute the 3D distance to.

        Returns
        -------
        float
            The 3D Euclidean distance between the two geometries.
        """
        return lib.sfcgal_geometry_distance_3d(self._geom, other._geom)

    @property
    @cond_icontract(lambda self: self.is_valid(), "require")
    def area(self) -> float:
        """
        Return the area of the geometry.

        This property returns the area of the geometry, applicable
        for surfaces like polygons.

        Returns
        -------
        float
            The area of the geometry.
        """
        return lib.sfcgal_geometry_area(self._geom)

    @property
    def is_empty(self) -> bool:
        """
        Check if the geometry is empty.

        Returns
        -------
        bool
            True if the geometry is empty, False otherwise.
        """
        return lib.sfcgal_geometry_is_empty(self._geom)

    @property
    def has_z(self) -> bool:
        """
        Check if the geometry has a Z component (3D geometry).

        Returns
        -------
        bool
            True if the geometry has a Z component, False otherwise.
        """
        return lib.sfcgal_geometry_is_3d(self._geom) == 1

    @property
    def has_m(self) -> bool:
        """
        Check if the geometry is measured (has an 'M' value).

        Returns
        -------
        bool
            True if the geometry is measured, False otherwise.
        """
        return lib.sfcgal_geometry_is_measured(self._geom) == 1

    @property
    def geom_type(self) -> str:
        """
        Return the type of the geometry as a string.

        Returns
        -------
        str
            The geometry type as a string (e.g., 'Point', 'Polygon').
        """
        geom_type = ffi.new("char **")
        geom_type_size = ffi.new("size_t *")
        lib.sfcgal_geometry_type(self._geom, geom_type, geom_type_size)
        ffi_geom_type = geom_type[0]

        if ffi_geom_type == ffi.NULL:
            return "Geometry"

        geom_type_str = ffi.string(ffi_geom_type).decode("utf-8")
        lib.sfcgal_free_buffer(ffi_geom_type)

        return geom_type_str

    @property
    def dimension(self) -> int:
        """
        Return the dimension of a given geometry as an integer.

        Returns
        -------
        int
            The dimension as an integer (0 : punctual, 1 : curve, …)
        """
        return lib.sfcgal_geometry_dimension(self._geom)

    def drop_z(self, inplace: bool = False) -> Optional[Geometry]:
        """
        Drop the z coordinate of the geometry

        Parameters
        ----------
        inplace : bool
            If False, return a copy. Otherwise, do operation in
            place and return None.
        Returns
        -------
        Geometry or None
            Geometry with the z coordinate dropped or None if
            inplace=True
        """
        if inplace:
            lib.sfcgal_geometry_drop_z(self._geom)
            return None
        else:
            new_geom = self.wrap()
            if new_geom:
                lib.sfcgal_geometry_drop_z(new_geom._geom)
            return new_geom

    def drop_m(self, inplace: bool = False) -> Optional[Geometry]:
        """
        Drop the m coordinate of the geometry

        Parameters
        ----------
        inplace : bool
            If False, return a copy. Otherwise, do operation in
            place and return None.
        Returns
        -------
        Geometry or None
            Geometry with the m coordinate dropped or None if
            inplace=True
        """
        if inplace:
            lib.sfcgal_geometry_drop_m(self._geom)
            return None
        else:
            new_geom = self.wrap()
            if new_geom:
                lib.sfcgal_geometry_drop_m(new_geom._geom)
            return new_geom

    def force_z(self, z: float = 0., inplace: bool = False) -> Optional[Geometry]:
        """
        Add a z-dimension to the geometry, initialized to a preset value.
        Existing Z values remains unchanged.

        Parameters
        ----------
        z: float
            z-value to use
        inplace : bool
            If False, return a copy. Otherwise, do operation in
            place and return None.
        Returns
        -------
        Geometry or None
            Geometry with the z coordinate set or None if
            inplace=True
        """
        if inplace:
            lib.sfcgal_geometry_force_z(self._geom, z)
            return None
        else:
            new_geom = self.wrap()
            if new_geom:
                lib.sfcgal_geometry_force_z(new_geom._geom, z)
            return new_geom

    def force_m(self, m: float = 0., inplace: bool = False) -> Optional[Geometry]:
        """
        Add a m-dimension to the geometry, initialized to a preset value.
        Existing M values remains unchanged.

        Parameters
        ----------
        m: float
            m-value to use
        inplace : bool
            If False, return a copy. Otherwise, do operation in
            place and return None.
        Returns
        -------
        Geometry or None
            Geometry with the m coordinate set or None if
            inplace=True
        """
        if inplace:
            lib.sfcgal_geometry_force_m(self._geom, m)
            return None
        else:
            new_geom = self.wrap()
            if new_geom:
                lib.sfcgal_geometry_force_m(new_geom._geom, m)
            return new_geom

    def swap_xy(self, inplace: bool = False) -> Optional[Geometry]:
        """
        Swap the x and y coordinates of the geometry

        Parameters
        ----------
        inplace : bool
            If False, return a copy. Otherwise, do operation in
            place and return None.
        Returns
        -------
        Geometry or None
            Geometry with the x and y coordinates swapped or None if
            inplace=True
        """
        if inplace:
            lib.sfcgal_geometry_swap_xy(self._geom)
            return None
        else:
            new_geom = self.wrap()
            if new_geom:
                lib.sfcgal_geometry_swap_xy(new_geom._geom)
            return new_geom

    @cond_icontract(lambda self: self.is_valid(), "require")
    def centroid(self, compute_2d_area: bool = False) -> Optional[Geometry]:
        """Return the centroid of the geometry.

        The result is the weighted centroid of a geometry. The implementation follows
        the PostGIS one (https://postgis.net/docs/ST_Centroid.html).

        The weight is computed either in the XY space or the 3D space depending on the
        value of `compute_2d_area` parameter. If the Z-component is ignored, the
        projected 2D geometries must be valid (vertical geometries will generate an
        error).

        Parameters
        ----------
        compute_2d_area: bool
            If True, the centroid is computed with respect to the area of 2D-projected
            geometries. Otherwise the centroid is computed with respect to the area of
            native 3D geometries. Warning: setting this parameter to True is not
            compatible with "vertical" geometries.

        Returns
        -------
        sfcgal.Point
            Centroid of the geometry

        """
        if compute_2d_area:
            geom = lib.sfcgal_geometry_centroid(self._geom)
        else:
            geom = lib.sfcgal_geometry_centroid_3d(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @property
    @cond_icontract(lambda self: self.is_valid(), "require")
    def area_3d(self) -> float:
        """
        Return the 3D area of the geometry.

        Returns
        -------
        float
            The 3D area of the geometry.
        """
        return lib.sfcgal_geometry_area_3d(self._geom)

    @property
    @cond_icontract(lambda self: self.is_valid(), "require")
    def volume(self) -> float:
        """
        Return the volume of the geometry.

        Returns
        -------
        float
            The volume of the geometry.
        """
        return lib.sfcgal_geometry_volume(self._geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def convexhull(self) -> Optional[Geometry]:
        """
        Compute the 2D convex hull of the geometry.

        Returns
        -------
        Geometry
            The convex hull of the geometry.
        """
        geom = lib.sfcgal_geometry_convexhull(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def convexhull_3d(self) -> Optional[Geometry]:
        """
        Compute the 3D convex hull of the geometry.

        Returns
        -------
        Geometry
            The 3D convex hull of the geometry.
        """
        geom = lib.sfcgal_geometry_convexhull_3d(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    def boundary(self) -> Optional[Geometry]:
        """
        Compute the boundary of the geometry.

        Returns
        -------
        Geometry
            The boundary of the geometry.
            The return type depends on the input:

            - ``Point`` / ``MultiPoint`` : empty geometry
            - ``LineString`` : ``MultiPoint`` (start/end), or empty if closed
            - ``Polygon`` : ``LineString``, or ``MultiLineString`` if interior rings
            - ``Triangle`` : ``LineString`` (closed ring of 3 edges)
            - ``MultiPolygon`` / ``PolyhedralSurface`` / ``TriangulatedSurface`` :
              ``MultiLineString`` of free edges, or empty if the surface is closed
            - ``GeometryCollection`` : not supported
            - ``Solid`` / ``MultiSolid`` : not supported
        """
        boundary = lib.sfcgal_geometry_boundary(self._geom)
        return Geometry.from_sfcgal_geometry(boundary)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def difference(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the difference between this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the difference with.

        Returns
        -------
        Geometry
            The resulting geometry after computing the difference.
        """
        geom = lib.sfcgal_geometry_difference(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def difference_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the difference between this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D difference with.

        Returns
        -------
        Geometry
            The resulting 3D geometry after computing the difference.
        """
        geom = lib.sfcgal_geometry_difference_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid(), "require")
    def intersects(self, other: Geometry) -> bool:
        """
        Check if this geometry intersects with another geometry in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check intersection with.

        Returns
        -------
        bool
            True if the geometries intersect, False otherwise.
        """
        return lib.sfcgal_geometry_intersects(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersects_3d(self, other: Geometry) -> bool:
        """
        Check if this geometry intersects with another geometry in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check intersection with.

        Returns
        -------
        bool
            True if the geometries intersect in 3D, False otherwise.
        """
        return lib.sfcgal_geometry_intersects_3d(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersection(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the intersection of this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the intersection with.

        Returns
        -------
        Geometry
            The resulting geometry after the intersection operation.
        """
        geom = lib.sfcgal_geometry_intersection(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersection_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the intersection of this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D intersection with.

        Returns
        -------
        Geometry
            The resulting geometry after the 3D intersection operation.
        """
        geom = lib.sfcgal_geometry_intersection_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def union(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the union of this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the union with.

        Returns
        -------
        Geometry
            The resulting geometry after the union operation.
        """
        geom = lib.sfcgal_geometry_union(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def union_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the union of this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D union with.

        Returns
        -------
        Geometry
            The resulting 3D geometry after the union operation.
        """
        geom = lib.sfcgal_geometry_union_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def covers(self, other: Geometry) -> bool:
        """
        Check if this geometry covers another geometry in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check coverage with.

        Returns
        -------
        bool
            True if this geometry covers the other geometry, False otherwise.
        """
        return lib.sfcgal_geometry_covers(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def covers_3d(self, other: Geometry) -> bool:
        """
        Check if this geometry covers another geometry in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check 3D coverage with.

        Returns
        -------
        bool
            True if this geometry covers the other geometry in 3D, False otherwise.
        """
        return lib.sfcgal_geometry_covers_3d(self._geom, other._geom) == 1

    @cond_icontract(lambda self: self.is_valid(), "require")
    def triangulate_2dz(self) -> Optional[Geometry]:
        """
        Compute a constrained Delaunay triangulation, preserving Z values.

        Returns
        -------
        Geometry
            The resulting triangulated geometry with Z values.
        """
        geom = lib.sfcgal_geometry_triangulate_2dz(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    @deprecated("tessellate_3d() is deprecated. Use tessellate() instead.")
    def tessellate_3d(self) -> Optional[Geometry]:
        """
        Perform tessellation on the geometry.

        Returns
        -------
        Geometry
            The tessellated geometry.
        """
        return self.tessellate()

    @cond_icontract(lambda self: self.is_valid(), "require")
    def tessellate(self) -> Optional[Geometry]:
        """
        Perform tessellation on the geometry.

        .. warning::
            **API break** since version 2.3:
            this method previously performed a constrained Delaunay
            triangulation (``triangulate_2dz``) followed by an
            intersection with the original geometry. It now calls the SFCGAL
            tessellation directly, without the intersection step.

        To reproduce the former behaviour:

            triangles = geom.triangulate_2dz()
            result = geom.intersection(triangles)

        Returns
        -------
        Geometry
            The tessellated geometry.
        """
        tessellation = lib.sfcgal_geometry_tessellate(self._geom)
        return Geometry.from_sfcgal_geometry(tessellation)

    def insert_points_within_tolerance(self, other: Geometry,
                                       tolerance: float) -> Optional[Geometry]:
        """
        Insert points from other geometry into self geometry within tolerance.
        This function densifies the base geometry by adding points from the other
        geometry where they are within the specified tolerance distance from the
        self geometry's segments.

        Parameters
        ----------
        other : Geometry
            The other geometry to insert points on self.
        tolerance : float
            Maximum distance for a point to be considered for insertion

        Returns
        -------
        Geometry
            The resulting geometry including points from other.
        """
        geom = lib.sfcgal_geometry_insert_points_within_tolerance(self._geom,
                                                                  other._geom,
                                                                  tolerance)
        return Geometry.from_sfcgal_geometry(geom)

    def force_lhr(self) -> Optional[Geometry]:
        """
        Force the geometry to have a left-hand rule (LHR) orientation.

        Returns
        -------
        Geometry
            The resulting geometry with LHR orientation.
        """
        geom = lib.sfcgal_geometry_force_lhr(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    def force_rhr(self) -> Optional[Geometry]:
        """
        Force the geometry to have a right-hand rule (RHR) orientation.

        Returns
        -------
        Geometry
            The resulting geometry with RHR orientation.
        """
        geom = lib.sfcgal_geometry_force_rhr(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    def is_simple(self) -> bool:
        """
        Test if the geometry is simple.

        Returns
        -------
        bool
            True if the geometry is simple, False otherwise.
        """
        return lib.sfcgal_geometry_is_simple(self._geom) != 0

    def is_simple_detail(self) -> Tuple[bool, str]:
        """
        Test if the geometry is simple and return details in case of
        complexity.

        Returns
        -------
        tuple
            - True if the geometry is simple, False otherwise.
            - If not simple, a string which contains the reason of the
              complexity
        """
        complex_reason = ffi.new("char **")
        lib.sfcgal_geometry_is_simple_detail(self._geom, complex_reason)

        ffi_complex_reason = complex_reason[0]

        # If ffi_complex_reason is Null, the geometry is simple.
        if ffi_complex_reason == ffi.NULL:
            return (True, "")

        complex_reason_str = ffi.string(ffi_complex_reason).decode("utf-8")
        lib.sfcgal_free_buffer(ffi_complex_reason)
        return (False, complex_reason_str)

    def is_valid(self) -> bool:
        """Check if the geometry is valid.

        The validity status updates the geometry validity flag.

        Returns
        -------
        bool
            True if the geometry is valid, False otherwise.
        """
        if self.validity_flag:
            return True
        sfcgal_validity = lib.sfcgal_geometry_is_valid(self._geom) != 0
        self.validity_flag = sfcgal_validity
        return sfcgal_validity

    def is_valid_detail(self) -> Tuple[Optional[str], None]:
        """
        Provide detailed information about the validity of the geometry.
        At the moment, the invalidity location is not returned (set to
        None) because it is not implemented by the C API.

        Returns
        -------
        str
            A string describing the reason if the geometry is invalid.
            If valid, returns None.
        """
        if self.validity_flag:
            # early-stop to avoid useless computation time in SFCGAL
            return (None, None)

        invalidity_reason = ffi.new("char **")
        invalidity_location = ffi.new("sfcgal_geometry_t **")
        lib.sfcgal_geometry_is_valid_detail(
            self._geom, invalidity_reason, invalidity_location
        )
        ffi_invalidity_reason = invalidity_reason[0]

        # If ffi_invalidity_reason is Null, the geometry is valid.
        if ffi_invalidity_reason == ffi.NULL:
            return (None, None)

        invalidity_reason_str = ffi.string(ffi_invalidity_reason).decode("utf-8")
        lib.sfcgal_free_buffer(ffi_invalidity_reason)

        ffi_invalidity_location = invalidity_location[0]
        if ffi_invalidity_location != ffi.NULL:
            lib.sfcgal_geometry_delete(ffi_invalidity_location)

        return (invalidity_reason_str, None)

    def is_closed(self) -> bool:
        """
        Check if the geometry is closed.
        Definition of "closed" varies by geometry type:
          - Point: Always closed
          - LineString: Closed if first and last points are identical
          - Polygon: Always closed (rings are closed by definition)
          - Triangle: Always closed
          - PolyhedralSurface: Closed if it forms a closed volume (no boundary edges)
          - TriangulatedSurface: Closed if it forms a closed volume
          - Solid: Always closed (by definition, but we test if the shells are closed)
          - MultiPoint: Always closed
          - MultiLineString: Closed if all LineStrings are closed
          - MultiPolygon: Always closed
          - MultiSolid: Always closed (by definition, cf Solid)
          - GeometryCollection: Closed if all contained geometries are closed

        Returns
        -------
        bool
            True if the geometry is closed, False otherwise.
        """
        return lib.sfcgal_geometry_is_closed(self._geom) == 1

    def is_planar(self) -> bool:
        """
        Check if the geometry is planar.

        Returns
        -------
        bool
            True if the geometry is planar, False otherwise.
        """
        return lib.sfcgal_geometry_is_planar(self._geom) == 1

    @cond_icontract(lambda self: self.is_valid(), "require")
    def orientation(self) -> int:
        """
        Get the orientation of the geometry.

        Returns
        -------
        int
            The orientation of the geometry.
        """
        return lib.sfcgal_geometry_orientation(self._geom)

    @cond_icontract(lambda self, r: self.is_valid(), "require")
    def round(self, r: int) -> Optional[Geometry]:
        """
        Round the geometry to a specified precision.

        Parameters
        ----------
        r : float
            The precision to which to round the geometry.

        Returns
        -------
        float
            The rounded geometry.
        """
        geom = lib.sfcgal_geometry_round(self._geom, r)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def minkowski_sum(self, other: Geometry) -> Optional[Geometry]:
        """
        Calculate the Minkowski sum of this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry to calculate the Minkowski sum with.

        Returns
        -------
        Geometry
            The resulting Minkowski sum geometry.
        """
        geom = lib.sfcgal_geometry_minkowski_sum(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, radius: self.is_valid(), "require")
    def offset_polygon(self, radius: float) -> Optional[Geometry]:
        """
        Create an offset polygon from the geometry.

        Parameters
        ----------
        radius : float
            The radius of the offset.

        Returns
        -------
        Geometry
            The resulting offset polygon geometry.
        """
        geom = lib.sfcgal_geometry_offset_polygon(self._geom, radius)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, extrude_x, extrude_y, extrude_z: self.is_valid(), "require"
    )
    def extrude(
            self, extrude_x: float, extrude_y: float, extrude_z: float
    ) -> Optional[Geometry]:
        """
        Extrude the geometry in the specified direction.

        Parameters
        ----------
        extrude_x : float
            The distance to extrude in the x direction.
        extrude_y : float
            The distance to extrude in the y direction.
        extrude_z : float
            The distance to extrude in the z direction.

        Returns
        -------
        Geometry
            The resulting extruded geometry.
        """
        geom = lib.sfcgal_geometry_extrude(self._geom, extrude_x, extrude_y, extrude_z)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def straight_skeleton(self) -> Optional[Geometry]:
        """
        Compute the straight skeleton of the geometry.

        Returns
        -------
        Geometry
            The resulting straight skeleton geometry.
        """
        geom = lib.sfcgal_geometry_straight_skeleton(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def straight_skeleton_distance_in_m(self) -> Optional[Geometry]:
        """
        Compute the straight skeleton distance in meters.

        Returns
        -------
        Geometry
            The resulting geometry representing the straight skeleton distance.
        """
        geom = lib.sfcgal_geometry_straight_skeleton_distance_in_m(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, height: (
            self.is_valid() and self.geom_type == "Polygon" and height != 0
        ),
        "require",
    )
    def extrude_straight_skeleton(self, height: float) -> Optional[Geometry]:
        """
        Extrude the geometry along its straight skeleton.

        Parameters
        ----------
        height : float
            The height to which the geometry will be extruded.

        Returns
        -------
        Geometry
            The resulting extruded geometry along the straight skeleton.
        """
        geom = lib.sfcgal_geometry_extrude_straight_skeleton(self._geom, height)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, building_height, roof_height: (
            self.is_valid() and self.geom_type == "Polygon" and roof_height != 0
        ),
        "require",
    )
    def extrude_polygon_straight_skeleton(
        self, building_height: float, roof_height: float
    ) -> Optional[Geometry]:
        """
        Extrude a polygon along its straight skeleton with specified building
        and roof heights.

        Parameters
        ----------
        building_height : float
            The height of the building.
        roof_height : float
            The height of the roof.

        Returns
        -------
        Geometry
            The resulting geometry with the specified building and roof heights.
        """
        geom = lib.sfcgal_geometry_extrude_polygon_straight_skeleton(
            self._geom, building_height, roof_height
        )
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, height, angles: (
            self.is_valid()
            and self.geom_type == "Polygon"
            and height != 0
            and (
                all(
                    [
                        0 < edge_angle <= 90
                        for ring_angle in angles
                        for edge_angle in ring_angle
                    ]
                )
                or all(
                    [
                        90 <= edge_angle < 180
                        for ring_angle in angles
                        for edge_angle in ring_angle
                    ]
                )
            )
        ),
        "require",
    )
    def extrude_straight_skeleton_with_angles(
        self,
        height: float,
        angles: list[list[float]],
    ) -> Optional[Geometry]:
        """
        Extrude the geometry along its straight skeleton using specific angles
        for each segment ring.

        Parameters
        ----------
        height : float
            The height to which the geometry will be extruded.
        angles : list of list of float
            Array of angles (in degrees) for each edge of each ring

        Returns
        -------
        Geometry
            The resulting extruded geometry along the straight skeleton.
        """

        angles_c = ffi.new(
            "double[]",
            [edge_angle for ring_angle in angles for edge_angle in ring_angle],
        )
        angles_per_ring = [len(ring) for ring in angles]
        angles_per_ring_c = ffi.new("size_t[]", angles_per_ring)
        geom = lib.sfcgal_geometry_extrude_straight_skeleton_with_angles(
            self._geom, height, angles_c, angles_per_ring_c, len(angles_per_ring)
        )
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self: (
            self.is_valid()
            and self.geom_type in ("MultiPolygon", "Polygon", "Triangle")
        ),
        "require",
    )
    def straight_skeleton_partition(self):
        """Returns the straight skeleton partition for the given Polygon

        Returns
        -------
        Geometry
            Partition of the Polygon straight skeleton
        """
        geom = lib.sfcgal_geometry_straight_skeleton_partition(self._geom, True)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def approximate_medial_axis(
            self, extend_to_edges: bool = False) -> Optional[Geometry]:
        """
        Compute the approximate medial axis of the geometry.

        Parameters
        ----------
        extend_to_edges : bool, optional
            Whether to extend end points to the polygon boundary (default is False).

        Returns
        -------
        Geometry
            The resulting geometry representing the approximate medial axis.
        """
        if extend_to_edges:
            geom = lib.sfcgal_geometry_projected_medial_axis(self._geom)
        else:
            geom = lib.sfcgal_geometry_approximate_medial_axis(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, start, end: (
            self.is_valid() and -1. <= start <= 1. and -1. <= end <= 1.
        ),
        "require",
    )
    @cond_icontract(lambda result: result.is_valid(), "ensure")
    def line_sub_string(self, start: float, end: float) -> Optional[Geometry]:
        """
        Extract a substring from the geometry represented as a line segment.

        Parameters
        ----------
        start : float
            The start parameter of the substring.
        end : float
            The end parameter of the substring.

        Returns
        -------
        Geometry
            The resulting substring geometry.
        """
        geom = lib.sfcgal_geometry_line_sub_string(self._geom, start, end)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, alpha=1.0, allow_holes=False: (
            self.is_valid() and alpha >= 0
        ),
        "require",
    )
    def alpha_shapes(
            self, alpha: float = 1.0, allow_holes: bool = False) -> Optional[Geometry]:
        """
        Compute the alpha shapes of the geometry.

        Parameters
        ----------
        alpha : float, optional
            The alpha parameter (default is 1.0).
        allow_holes : bool, optional
            Whether to allow holes in the alpha shapes (default is False).

        Returns
        -------
        Geometry
            The resulting alpha shapes geometry.
        """
        if "MSC" in compiler:
            raise NotImplementedError(
                "Alpha shapes methods is not available on Python versions using MSVC "
                "compiler. See: https://github.com/CGAL/cgal/issues/7667"
            )
        geom = lib.sfcgal_geometry_alpha_shapes(self._geom, alpha, allow_holes)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, allow_holes=False, nb_components=1: (
            self.is_valid() and nb_components >= 0
        ),
        "require",
    )
    def optimal_alpha_shapes(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the optimal alpha shapes of the geometry.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the optimal alpha shapes (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting optimal alpha shapes geometry.
        """
        if "MSC" in compiler:
            raise NotImplementedError(
                "Alpha shapes methods is not available on Python versions using MSVC "
                "compiler. See: https://github.com/CGAL/cgal/issues/7667"
            )
        geom = lib.sfcgal_geometry_optimal_alpha_shapes(
            self._geom, allow_holes, nb_components
        )
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, relative_alpha, relative_offset=0: (
            self.is_valid() and relative_alpha > 0 and relative_offset >= 0
        ),
        "require",
    )
    def alpha_wrapping_3d(
            self, relative_alpha: int, relative_offset: int = 0) -> Optional[Geometry]:
        """
        Compute the 3D alpha wrapping of a geometry

        Parameters
        ----------
        relative_alpha : int
            The relative_alpha parameter
        relative_offset : int, optional
            The alpha parameter (default is 0).
            If relative_offset is equal, it is automatically computed
            from the relative_alpha parameter.

        Returns
        -------
        Geometry
            The resulting 3D alpha wrapping geometry as a PolyhedralSurface.
        """
        geom = lib.sfcgal_geometry_alpha_wrapping_3d(
            self._geom, relative_alpha, relative_offset)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def y_monotone_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the Y-monotone partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting Y-monotone partition geometry.
        """
        geom = lib.sfcgal_y_monotone_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def approx_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the approximate convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting approximate convex partition geometry.
        """
        geom = lib.sfcgal_approx_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def greene_approx_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the Greene's approximate convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting Greene's approximate convex partition geometry.
        """
        geom = lib.sfcgal_greene_approx_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def optimal_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the optimal convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting optimal convex partition geometry.
        """
        geom = lib.sfcgal_optimal_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, other: (
            self.is_valid()
            and self.geom_type == "Polygon"
            and other.is_valid()
            and other.geom_type == "Point"
            and self.intersects(other)
        ),
        "require",
    )
    def point_visibility(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the visibility of a point from a polygon geometry.

        Parameters
        ----------
        other : Geometry
            A point geometry from which the visibility is computed.

        Returns
        -------
        Geometry
            The resulting geometry representing the visibility from the point to
            the polygon.
        """
        geom = lib.sfcgal_geometry_visibility_point(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, other_a, other_b: (
            self.is_valid()
            and self.geom_type == "Polygon"
            and other_a.is_valid()
            and other_a.geom_type == "Point"
            and other_b.is_valid()
            and other_b.geom_type == "Point"
            and self.has_exterior_edge(other_a, other_b)
        ),
        "require",
    )
    def segment_visibility(
            self, other_a: Geometry, other_b: Geometry) -> Optional[Geometry]:
        """
        Compute the visibility of a segment between two points from a polygon geometry.

        Parameters
        ----------
        other_a : Geometry
            The first point geometry defining one endpoint of the segment.
        other_b : Geometry
            The second point geometry defining the other endpoint of the segment.

        Returns
        -------
        Geometry
            The resulting geometry representing the visibility along the segment between
            the two points.
        """
        geom = lib.sfcgal_geometry_visibility_segment(
            self._geom, other_a._geom, other_b._geom
        )
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("translate_2d() is deprecated. Use translate() instead.")
    def translate_2d(self, dx: float = 0, dy: float = 0) -> Optional[Geometry]:
        """
        This method is an alias for the `translate` function.

        .. deprecated:: 2.0.0
                `translate_2d` will be removed in v3.0.0, it is replaced by
                `translate` in order to be consistent in the function naming.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector

        Returns
        -------
        Geometry
            A 2D geometry translated from the current geometry
        """
        return self.translate(dx, dy)

    def translate(self, dx: float = 0, dy: float = 0) -> Optional[Geometry]:
        """Translate a geometry by a 2D vector, hence producing a
        2D-geometry as an output.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector

        Returns
        -------
        Geometry
            A 2D geometry translated from the current geometry
        """
        translated_geom = lib.sfcgal_geometry_translate_2d(self._geom, dx, dy)
        return Geometry.from_sfcgal_geometry(translated_geom)

    def translate_3d(
            self, dx: float = 0, dy: float = 0, dz: float = 0) -> Optional[Geometry]:
        """
        Translate a geometry by a 3D vector, hence producing a 3D-geometry as an output.

        If the current geometry is 2D, the starting Z coordinates is assumed to be 0.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector
        dz : float, optional
            z component of the translation vector

        Returns
        -------
        Geometry
            A 3D geometry translated from the current geometry
        """
        translated_geom = lib.sfcgal_geometry_translate_3d(self._geom, dx, dy, dz)
        return Geometry.from_sfcgal_geometry(translated_geom)

    def scale_uniform(self, factor: float = 1.) -> Optional[Geometry]:
        """Scale a geometry by a given factor

        Parameters
        ----------
        factor : float, optional
            Scaling factor, 1. by default (identity scale)

        Returns
        -------
        Geometry
            Scaled geometry
        """
        return self.scale(factor, factor, factor)

    def scale(
            self, fx: float = 1., fy: float = 1., fz: float = 1.) -> Optional[Geometry]:
        """Scale a geometry by different factors for each dimension

        Parameters
        ----------
        fx : float, optional
            Scaling factor for x dimension, 1. by default (identity scale)
        fy : float, optional
            Scaling factor for y dimension, 1. by default (identity scale)
        fz : float, optional
            Scaling factor for z dimension, 1. by default (identity scale)

        Returns
        -------
        Geometry
            Scaled geometry
        """
        geom = lib.sfcgal_geometry_scale_3d(self._geom, fx, fy, fz)
        return Geometry.from_sfcgal_geometry(geom)

    def scale_around_center(
            self, fx: float, fy: float, fz: float, cx: float, cy: float, cz: float
    ) -> Optional[Geometry]:
        """
        Scale a geometry by different factors for each dimension around a center point

        Parameters
        ----------
        fx : float
            Scaling factor for x dimension
        fy : float
            Scaling factor for y dimension
        fz : float
            Scaling factor for z dimension
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point
        cz : float
            Z-coordinate of the center point

        """
        geom = lib.sfcgal_geometry_scale_3d_around_center(
            self._geom, fx, fy, fz, cx, cy, cz
        )
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_around_2d_point() is deprecated. Use rotate() instead.")
    def rotate_around_2d_point(
        self, angle: float, cx: float, cy: float
    ) -> Optional[Geometry]:
        """
        Rotates a geometry around a specified point by a given angle

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_2d(self._geom, angle, cx, cy)
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_around_3d_axis() is deprecated. Use rotate_3d() instead.")
    def rotate_around_3d_axis(
        self, angle: float, ax: float, ay: float, az: float
    ) -> Optional[Geometry]:
        """
        Rotates a 3D geometry around a specified axis by a given angle

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        ax : float
            X-coordinate of the axis vector
        ay : float
            Y-coordinate of the axis vector
        az : float
            Z-coordinate of the axis vector

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_3d(self._geom, angle, ax, ay, az)
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_around_3d_center() is deprecated. Use rotate_3d() instead.")
    def rotate_3d_around_center(
        self,
        angle: float,
        ax: float,
        ay: float,
        az: float,
        cx: float,
        cy: float,
        cz: float,
    ) -> Optional[Geometry]:
        """
        Rotates a 3D geometry around a specified axis and center point by a given

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        ax : float
            X-coordinate of the axis vector
        ay : float
            Y-coordinate of the axis vector
        az : float
            Z-coordinate of the axis vector
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point
        cz : float
            Z-coordinate of the center point

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_3d_around_center(
            self._geom, angle, ax, ay, az, cx, cy, cz
        )
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_x() is deprecated. Use rotate_3d_x() instead.")
    def rotate_x(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the X axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_x(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_y() is deprecated. Use rotate_3d_y() instead.")
    def rotate_y(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the Y axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_y(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    @deprecated("rotate_z() is deprecated. Use rotate_3d_z() instead.")
    def rotate_z(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the Z axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_z(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate(
            self, angle: float = 0.,
            center: Optional[Point] = None) -> Optional[Geometry]:
        """
        Rotates a geometry in 2D by a given angle

        If the center is not provided, the geometry is rotated
        around the origin (0, 0).

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians
        center: Point, defaults to the origin (0, 0).
            Rotation center

        Returns
        -------
        Geometry
            The rotated geometry
        """
        from .point import Point

        if center is None:
            center = Point(0, 0)

        geom = lib.sfcgal_geometry_rotate_2d(self._geom, angle, center.x, center.y)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_3d(
            self, angle: float, axis: Vector3D, center: Optional[Point] = None
    ) -> Optional[Geometry]:
        """
        Rotates a geometry in 3D around an axis by a given angle

        If the center is not provided, the geometry is rotated
        around the origin (0, 0, 0).

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        axis: Vector3D
            Rotation axis
        center: Point, defaults to the origin (0, 0, 0).
            Rotation center

        Returns
        -------
        Geometry
            The rotated geometry
        """
        from .point import Point

        if center is None:
            center = Point(0, 0, 0)

        geom = lib.sfcgal_geometry_rotate_3d_around_center(
            self._geom, angle, axis.x, axis.y, axis.z, center.x, center.y, center.z)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_3d_x(
            self, angle: float, center: Optional[Point] = None) -> Optional[Geometry]:
        """
        Rotates a geometry in 3D around the X axis by a given angle

        If the center is not provided, the geometry is rotated
        around the origin (0, 0, 0).

        Shorthand for rotate_3d(angle, UNIT_X, center).

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        center: Point, defaults to the origin (0, 0, 0).
            Rotation center

        Returns
        -------
        Geometry
            The rotated geometry
        """
        return self.rotate_3d(angle, UNIT_X, center)

    def rotate_3d_y(
            self, angle: float, center: Optional[Point] = None) -> Optional[Geometry]:
        """
        Rotates a geometry in 3D around the Y axis by a given angle

        If the center is not provided, the geometry is rotated
        around the origin (0, 0, 0).

        Shorthand for rotate_3d(angle, UNIT_Y, center).

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        center: Point, defaults to the origin (0, 0, 0).
            Rotation center

        Returns
        -------
        Geometry
            The rotated geometry
        """
        return self.rotate_3d(angle, UNIT_Y, center)

    def rotate_3d_z(
            self, angle: float, center: Optional[Point] = None) -> Optional[Geometry]:
        """
        Rotates a geometry in 3D around the Z axis by a given angle

        If the center is not provided, the geometry is rotated
        around the origin (0, 0, 0).

        Shorthand for rotate_3d(angle, UNIT_Z, center).

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        center: Point, defaults to the origin (0, 0, 0).
            Rotation center

        Returns
        -------
        Geometry
            The rotated geometry
        """
        return self.rotate_3d(angle, UNIT_Z, center)

    @cond_icontract(lambda self, tolerance: (self.is_valid() and tolerance > 0),
                    "require")
    def simplify(self, tolerance: float, preserve_topology: bool) -> Optional[Geometry]:
        """
        Compute the simplication of the geometry.

        Parameters
        ----------
        tolerance : float
            The simplification threshold.
        preserve_topology : bool
            Preserve topology or not.

        Returns
        -------
        Geometry
            The simplified geometry.
        """
        geom = lib.sfcgal_geometry_simplify(self._geom, tolerance, preserve_topology)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, edge_count, edge_ratio, strategy: self.is_valid(), "require"
    )
    @cond_icontract(
        lambda self, edge_count, edge_ratio, strategy: (
            edge_count is None or edge_count > 0
        ),
        "require",
    )
    @cond_icontract(
        lambda self, edge_count, edge_ratio, strategy: (
                edge_ratio is None or (edge_ratio > 0 and edge_ratio < 1)
        ),
        "require",
    )
    @cond_icontract(
        lambda self, edge_count, edge_ratio, strategy: (
                isinstance(strategy, SimplificationStrategy)
                or (isinstance(strategy, int) and strategy in (0, 1, 2))
        ),
        "require",
    )
    def simplify_surface(
        self,
        edge_count: Optional[int] = None,
        edge_ratio: Optional[float] = None,
        strategy: Union[
            SimplificationStrategy, int
        ] = SimplificationStrategy.EDGE_LENGTH,
    ) -> Optional[Geometry]:
        """Simplify a surface mesh using CGAL edge collapse algorithm.

        Two stop predicates may be used: an edge quantity (between 0 and the edge amount
        ) or a ratio regarding the total amount of edges (between 0 and 1).

        Several CGAL strategies may be used in order to remove edges:

        - the default one uses edge length as cost function and midpoint placement for
          vertex positioning. This strategy is compatible with exact kernels and
          provides good simplification results while maintaining geometric accuracy.

        - the Garland-Heckbert strategy uses quadric error metrics for cost calculation
          and optimal vertex placement. This strategy requires Eigen support and uses
          inexact constructions for improved performance on large meshes.

        - the Lindstrom-Turk strategy uses cost and placement policies optimized for
          preserving volume and boundary features. This strategy requires Eigen support
          and uses inexact constructions for improved performance on complex meshes.

        The Garland-Heckbert and the Lindstrom-Turk strategies needs SFCGAL to be built
        with SFCGAL_WITH_EIGEN compilation option. If the function is called with these
        strategies, whilst using a version of SFCGAL that is not compiled with the
        SFCGAL_WITH_EIGEN option, SFCGAL will return a null pointer, traduced as a None
        value on the PySFCGAL-side.

        Parameters
        ----------
        edge_count : int
            The targeted amount of edges in the output geometry. If it is greater than
            the actual geometry edge quantity, the function has no effect. The edge
            count stop predicates is used by default is this parameter is not None.
        edge_ratio : float
            The targeted edge ratio to keep in the output geometry. It should be
            defined between 0 and 1. The edge ratio is not used if edge_count is not
            None.
        strategy : SimplificationStrategy
            Either 0 (EDGE_LENGTH, default value), 1 (Garland-Heckbert) or 2
            (Lindstrom-Turk).

        Returns
        -------
        A simplified geometry, with less edge than the original geometry.

        """
        if isinstance(strategy, SimplificationStrategy):
            strategy = strategy.value
        if edge_count is not None:
            geom = lib.sfcgal_geometry_simplify_surface_edge_count(
                self._geom, edge_count, strategy
            )
        elif edge_ratio is not None:
            geom = lib.sfcgal_geometry_simplify_surface_edge_ratio(
                self._geom, edge_ratio, strategy
            )
        else:
            return None
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, plane_point, plane_normal, close_geometries: (
            self.is_valid()
            and self.geom_type in ("PolyhedralSurface", "Solid", "TriangulatedSurface")
        ),
        "require",
    )
    def split_3d(
            self,
            plane_point: Point,
            plane_normal: Vector3D,
            close_geometries: bool = True
    ) -> Optional[GeometryCollection]:
        """
        Split a geometry by a 3D plane.

        The splitting plane is defined by a point lying on the plane and
        a normal vector. The result is returned as a geometry collection
        containing the geometries located on each side of the plane, or
        an empty GeometryCollection if the plane does not intersect the
        geometry.

        Parameters
        ----------
        plane_point : Point
            A point belonging to the splitting plane.
        plane_normal : Vector3D
            The normal vector defining the orientation of the splitting
            plane.
        close_geometries : bool, default to True
            If ``True``, generated geometries are closed when possible.

        Returns
        -------
        GeometryCollection
            A geometry collection containing the split parts, or an
            empty GeometryCollection if the plane does not intersect the
            geometry.
        """
        from .collection import GeometryCollection

        split_geom = lib.sfcgal_geometry_split_3d(
            self._geom, plane_point.x, plane_point.y, plane_point.z, plane_normal.x,
            plane_normal.y, plane_normal.z, close_geometries)
        return cast(
            GeometryCollection, Geometry.from_sfcgal_geometry(split_geom))

    def write_vtk(self, filename: str) -> None:
        """
        Export the geometry to a VTK file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_vtk_file(self._geom, bytes(filename, 'utf-8'))

    def to_vtk(self) -> str:
        """
        Export the geometry to a VTK string, i.e. basically the content of a VTK file.

        Returns
        -------
        str
            VTK representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_vtk(self._geom, buf, length)
            vtk_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return vtk_string

    @staticmethod
    def read_obj(filename: str) -> Optional[Geometry]:
        """Parse an OBJ file into a Geometry object.

        This function takes an OBJ file, read it and converts its content into
        a `Geometry` object by utilizing the SFCGAL library's OBJ parsing capabilities.

        Parsing OBJ files creates 3D geometries with the following types, depending on
        the OBJ content:

        - OBJ with faces: Tin if all faces are triangular, PolyhedralSurface otherwise;
        - OBJ with lines: MultiLineString;
        - OBJ with points: MultiPoint.

        Parameters
        ----------
        filename : str
            The name of the OBJ file that contains the geometry.

        Returns
        -------
        Optional[Geometry]
            A `Geometry` object parsed from the OBJ string.

        """
        filename_bytes = bytes(filename, encoding="utf-8")
        geom = lib.sfcgal_io_read_obj_file(filename_bytes)
        return Geometry.from_sfcgal_geometry(geom)

    @staticmethod
    def from_obj(obj_str: str) -> Optional[Geometry]:
        """Parse an OBJ representation into a Geometry object.

        This function takes an OBJ string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's OBJ parsing capabilities.

        Parsing OBJ strings creates 3D geometries with the following types, depending
        on the OBJ content:

        - OBJ with faces: Tin if all faces are triangular, PolyhedralSurface otherwise;
        - OBJ with lines: MultiLineString;
        - OBJ with points: MultiPoint.

        Parameters
        ----------
        obj_str : str
            The OBJ string representing the geometry.

        Returns
        -------
        Optional[Geometry]
            A `Geometry` object parsed from the OBJ string.

        """
        obj_bytes = bytes(obj_str, encoding="utf-8")
        geom = lib.sfcgal_io_read_obj(obj_bytes, len(obj_bytes))
        return Geometry.from_sfcgal_geometry(geom)

    def write_obj(self, filename: str) -> None:
        """
        Export the geometry to a OBJ file.

        Notes
        -----
        The OBJ export does not preserve polygon holes. Geometries
        containing holes should be triangulated beforehand using
        `tesselate` if hole information needs to be preserved in the
        exported mesh.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_obj_file(self._geom, bytes(filename, 'utf-8'))

    def to_obj(self) -> str:
        """
        Export the geometry to a OBJ string, i.e. basically the content of a OBJ file.

        Notes
        -----
        The OBJ export does not preserve polygon holes. Geometries
        containing holes should be triangulated beforehand using
        `tesselate` if hole information needs to be preserved in the
        exported mesh.

        Returns
        -------
        str
            OBJ representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_obj(self._geom, buf, length)
            obj_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return obj_string

    def write_stl(self, filename: str) -> None:
        """
        Export the geometry to a STL file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_stl_file(self._geom, bytes(filename, 'utf-8'))

    def to_stl(self) -> str:
        """
        Export the geometry to a STL string, i.e. basically the content of a STL file.

        Returns
        -------
        str
            STL representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_stl(self._geom, buf, length)
            stl_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return stl_string

    def __del__(self):
        if self._owned and hasattr(self, "_geom"):
            # only free geometries owned by the class
            # this isn't the case when working with geometries contained by
            # a collection (e.g. a GeometryCollection)
            lib.sfcgal_geometry_delete(self._geom)

    def __str__(self):
        return self.to_wkt(8)

    def wrap(self) -> Optional[Geometry]:
        """Wrap the SFCGAL geometry attribute of the current instance in a new geometry
        instance. This method produces a deep copy of the geometry instance.

        Returns
        -------
        Geometry
            A cloned Geometry of the current instance

        """
        return Geometry.from_sfcgal_geometry(lib.sfcgal_geometry_clone(self._geom))

    @staticmethod
    def from_sfcgal_geometry(
            geom: ffi.CData, owned: bool = True,
            parent: Optional[Geometry] = None) -> Optional[Geometry]:
        """Wrap the SFCGAL geometry passed as a parameter in a new geometry instance.

        This method allows to build a new Python object from a SFCGAL geometry (which
        is basically a C pointer).

        Parameters
        ----------
        geom : _cffi_backend._CDatabase
            SFCGAL geometry that will be used as an attribute in the new geometry
            instance
        owned : bool
            If True, the new Geometry owns the SFCGAL pointer. Be careful, if a SFCGAL
            pointer is owned by several Geometry instances, there might be some trouble
            after removing one of them (or after the garbage collector action).

        parent : Optional[Geometry], default None
            Optional parent Geometry that this geometry depends on.
            This ensures that the parent geometry is not garbage collected by the Python
            interpreter while it is still in use.
            For example, a point extracted from a linestring.

        Returns
        -------
        Geometry
            A Geometry instance built from the SFCGAL geometry parameter.

        """
        # Lazy import that avoids circular imports between this module and the other
        # geometry modules
        from .registry import geom_type_to_cls

        if geom == ffi.NULL:
            return None
        geom_type_id = lib.sfcgal_geometry_type_id(geom)
        if geom_type_id not in geom_type_to_cls:
            return None
        cls = geom_type_to_cls[geom_type_id]
        geometry: Geometry = object.__new__(cls)
        geometry._geom = geom
        geometry._owned = owned
        geometry._parent = parent
        return geometry

    def to_coordinates(self):
        """Generates the coordinates of the Geometry.

        Raises
        ------
        NotImplementedError
            The method must be implemented only in child classes.
        """
        raise NotImplementedError(
            "to_coordinates is implemented only for child classes!"
        )

    def to_dict(self) -> dict:
        """Generates a geojson-like dictionary that represents the Geometry.

        This dictionary contains a 'type' key which depicts the geometry type
        (e.g. Point, MultiLineString, Tin, ...) and a 'coordinates' key that contains
        the geometry point coordinates.

        """
        return {"type": self.geom_type, "coordinates": self.to_coordinates()}

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Optional[Geometry]:
        """Instantiates a Geometry starting from a list of coordinates.

        The geometry class may be Point, LineString, Polygon, ...

        Parameters
        ----------
        coordinates : list
            Geometry coordinates, the list structure depends on the geometry type.

        Returns
        -------
        Geometry
            An instance of the corresponding geometry type
        """
        return cls(coordinates)  # type: ignore

    @classmethod
    def from_dict(cls, geojson_data: dict) -> Optional[Geometry]:
        """Instantiates a Geometry starting from a geojson-like dictionnary.

        The dictionary must contain 'type' and 'coordinates' keys; the 'type' value
        should be a valid geometry descriptor.

        The geometry class with which the method is called may be Point, LineString,
        Polygon, ...

        Parameters
        ----------
        geojson_data : dict
            Geometry description, in a geojson-like format

        Returns
        -------
        Geometry
            An instance of the corresponding geometry type
        """
        if geojson_data.get("type") is None:
            raise KeyError("There is no 'type' key in the provided data.")
        if geojson_data.get("coordinates") is None:
            raise KeyError("There is no 'coordinates' key in the provided data.")
        return cls.from_coordinates(geojson_data["coordinates"])

    @staticmethod
    def from_wkt(wkt: Optional[str]) -> Optional[Geometry]:
        """Parse a Well-Known Text (WKT) representation into a Geometry object.

        This function takes a WKT string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's WKT parsing capabilities.

        Parameters
        ----------
        wkt : str
            The Well-Known Text (WKT) string representing the geometry.

        Returns
        -------
        Geometry
            A `Geometry` object parsed from the WKT string.

        """
        if not wkt:
            return None

        sfcgal_geom = Geometry.sfcgal_geom_from_wkt(wkt)
        return Geometry.from_sfcgal_geometry(sfcgal_geom)

    @staticmethod
    def sfcgal_geom_from_wkt(wkt: str) -> ffi.CData:
        """
        Internal function to read Well-Known Text (WKT) and return the
        SFCGAL geometry object.

        This function converts the WKT string into a UTF-8 encoded byte string,
        and uses the SFCGAL library to create a geometry object from the WKT.

        Parameters
        ----------
        wkt : str
            The Well-Known Text (WKT) string representing the geometry.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        wkt_bytes = bytes(wkt, encoding="utf-8")
        return lib.sfcgal_io_read_wkt(wkt_bytes, len(wkt_bytes))

    @staticmethod
    def from_wkb(wkb: Union[bytes, bytearray]) -> Optional[Geometry]:
        """
        Parse a Well-Known Binary (WKB) representation into a Geometry object.

        This function takes a WKB byte string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's WKB parsing capabilities.

        Parameters
        ----------
        wkb : bytes
            The Well-Known Binary (WKB) byte string representing the geometry.

        Returns
        -------
        Geometry
            A `Geometry` object parsed from the WKB byte string.
        """
        sfcgal_geom = Geometry.sfcgal_geom_from_wkb(wkb)
        return Geometry.from_sfcgal_geometry(sfcgal_geom)

    @staticmethod
    def sfcgal_geom_from_wkb(wkb: Union[str, bytes, bytearray]) -> ffi.CData:
        """Internal function to read a Well-Known Binary (WKB) representation
        and return the SFCGAL geometry object.

        This function accepts a WKB representation in either binary format
        (bytes or bytearray) or hexadecimal string format,
        converts it into a UTF-8 encoded byte string, and uses the SFCGAL
        library to generate the corresponding geometry object.

        Parameters
        ----------
        wkb : bytes, bytearray, or str
            The Well-Known Binary (WKB) data representing the geometry.
            - If a `bytes` or `bytearray` object is provided, it is automatically
            converted to a hexadecimal string.
            - If a `str` is provided, it must already be a hexadecimal string.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        if isinstance(wkb, (bytes, bytearray)):
            wkb = wkb.hex()
        elif not isinstance(wkb, str):
            raise TypeError("WKB must be a hexadecimal str or data binary")
        wkb = bytes(wkb, encoding="utf-8")
        return lib.sfcgal_io_read_wkb(wkb, len(wkb))

    def to_wkt(self, decim: int = -1) -> str:
        """Convert a geometry object into its Well-Known Text (WKT) representation.

        This function takes a geometry object and returns its WKT representation as a
        string.
        If the `decim` parameter is provided and is non-negative, the WKT will include
        a specific number of decimal places.

        Parameters
        ----------
        decim : int, optional
            The number of decimal places to include in the WKT output.
            If `decim` is negative (default), the WKT is returned without a specific
            decimal precision.

        Returns
        -------
        str
            The Well-Known Text (WKT) representation of the geometry.

        """
        wkt = ""
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_text_decim(self._geom, decim, buf, length)
            wkt = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return wkt

    def to_wkb(self, as_hex: bool = False) -> str:
        """Convert a geometry object into its Well-Known Binary (WKB) or Hexadecimal WKB
        representation.

        This function takes a geometry object and returns its WKB representation as a
        binary string, or as a hexadecimal string if `as_hex` is set to True. It handles
        memory allocation for the generated WKB and ensures that memory is properly
        freed after use.

        Parameters
        ----------
        as_hex : bool, optional
            If True, the function returns the geometry's WKB as a hexadecimal string.
            If False (default), the WKB is returned as a binary string.

        Returns
        -------
        Union[str, bytes]
            WKB representation of the geometry

        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            if as_hex:
                lib.sfcgal_geometry_as_hexwkb(self._geom, buf, length)
            else:
                lib.sfcgal_geometry_as_wkb(self._geom, buf, length)

            wkb = ffi.buffer(buf[0], length[0])[:]
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return wkb.decode("utf-8") if as_hex else wkb

    @staticmethod
    def from_geojson(geojson: Optional[str]) -> Optional[Geometry]:
        """Parse a GeoJSON string representation into a Geometry object.

        This function takes a GeoJSON string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's GeoJSON parsing capabilities.

        Parameters
        ----------
        geojson : str
            The GeoJSON string representing the geometry.

        Returns
        -------
        Geometry
            A `Geometry` object parsed from the GeoJSON string.

        """
        if not geojson:
            return None

        sfcgal_geom = Geometry.sfcgal_geom_from_geojson(geojson)
        return Geometry.from_sfcgal_geometry(sfcgal_geom)

    @staticmethod
    def sfcgal_geom_from_geojson(geojson: str) -> ffi.CData:
        """
        Internal function to read a GeoJSON string and return the SFCGAL geometry
        object.

        This function converts the GeoJSON string into a UTF-8 encoded byte string,
        and uses the SFCGAL library to create a geometry object from the GeoJSON.

        Parameters
        ----------
        geojson : str
            The GeoJSON string representing the geometry.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        geojson_bytes = bytes(geojson, encoding="utf-8")
        return lib.sfcgal_io_read_geojson(geojson_bytes, len(geojson_bytes))

    @staticmethod
    def read_geojson(filename: str) -> Optional[Geometry]:
        """Read a GeoJSON file into a Geometry object.

        This function reads a GeoJSON file and converts its content into a `Geometry`
        object.

        Parameters
        ----------
        filename : str
            The name of the GeoJSON file that contains the geometry.

        Returns
        -------
        Optional[Geometry]
            A `Geometry` object parsed from the GeoJSON file.

        """
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return Geometry.from_geojson(content)

    def to_geojson(
        self, strict: bool = False, precision: int = 8, include_bbox: bool = False
    ) -> str:
        """Convert a geometry object into a GeoJSON string representation.

        This function takes a geometry object and returns its GeoJSON representation as
        a string.

        Parameters
        ----------
        strict : bool
            If True, output strictly RFC 7946 compliant GeoJSON. Non-standard types
            (TIN, Solid, etc.) are converted to standard types. If False, use SFCGAL
            type names as extensions (allows round-trip).
        precision : int
            Number of decimal places for coordinates. -1 means full precision.
        include_bbox : bool
            Include bounding box in output.

        Returns
        -------
        str
            The GeoJSON representation of the geometry.

        """
        geojson = ""
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_geojson(
                self._geom, strict, precision, include_bbox, buf, length
            )
            geojson = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return geojson

    def write_geojson(self, filename: str) -> None:
        """Export the geometry to a GeoJSON file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.to_geojson())
