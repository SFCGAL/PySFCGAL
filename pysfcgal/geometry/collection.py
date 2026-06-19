"""Simple Feature collection geometries.

One denotes GeometryCollection, MultiPoint, MultiLineString, MultiPolygon and
MultiSolid.

"""


from __future__ import annotations

from typing import Tuple, cast

from .._contracts import cond_icontract
from .._deprecated import deprecated
from .._sfcgal import ffi, lib
from .curve import LineString
from .geometry import Geometry
from .point import Point
from .surface import Polygon
from .volume import Solid

__all__ = [
    "GeometrySequence",
    "GeometryCollection",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "MultiSolid",
]


class GeometrySequence:
    def __init__(self, parent):
        """Initialize the GeometrySequence with a parent GeometryCollection.

        Parameters
        ----------
        parent : GeometryCollectionBase
            The parent geometry collection that this sequence belongs to.
        """
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __iter__(self):
        """Iterate over the geometries in the sequence.

        Yields
        ------
        Geometry
            Each geometry in the sequence as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
                owned=False, parent=self._parent,
            )

    def __len__(self):
        """Get the number of geometries in the sequence.

        Returns
        -------
        int
            The number of geometries in the collection.
        """
        return lib.sfcgal_geometry_num_geometries(self._parent._geom)

    def __get_geometry_n(self, n: int) -> Geometry | None:
        """Retrieve the n-th geometry in the sequence.

        Parameters
        ----------
        n : int
            The index of the geometry to retrieve.

        Returns
        -------
        Geometry
            The geometry at the specified index.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
            owned=False, parent=self._parent,
        )

    def __getitem__(self, key):
        """Get a geometry (or several) within the sequence, identified through an index
        or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the geometry or geometries to recover.

        Returns
        -------
        Geometry or list of Geometry
            The geometry or list of geometries at the specified index or slice.
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

    def __eq__(self, other: object) -> bool:
        """Check equality between this geometry sequence and another.

        Parameters
        ----------
        other : GeometrySequence
            The other geometry sequence to compare.

        Returns
        -------
        bool
            True if both geometry sequences are equal, False otherwise.
        """
        if not isinstance(other, GeometrySequence):
            return False
        return self[:] == other[:]


class GeometryCollectionBase(Geometry):
    @property
    def geoms(self):
        """Return the geometries in the collection.

        Returns
        -------
        GeometrySequence
            A sequence of geometries contained in this collection.
        """
        return GeometrySequence(self)

    def __len__(self):
        """Return the number of geometries in the collection.

        Returns
        -------
        int
            The number of geometries in the collection.
        """
        return len(self.geoms)

    def __iter__(self):
        """Iterate over the geometries in the collection.

        Yields
        ------
        Geometry
            Each geometry in the collection.
        """
        return self.geoms.__iter__()

    def __getitem__(self, index):
        """Get a geometry (or several) within the collection, identified through an
        index.

        Raises an IndexError if the index is invalid for the geometry collection.

        Parameters
        ----------
        index : int
            Index of the geometry to recover.

        Returns
        -------
        Geometry
            The geometry at the specified index.
        """
        return self.geoms[index]

    def __eq__(self, other: object) -> bool:
        """Check if two geometry collections are equal based on their geometries.

        Parameters
        ----------
        other : GeometryCollectionBase
            The other geometry collection to compare.

        Returns
        -------
        bool
            True if both collections contain the same geometries, False otherwise.
        """
        if not isinstance(other, GeometryCollectionBase):
            return False
        return self.geoms == other.geoms

    def to_coordinates(self):
        """Generates the coordinates for every geometry collection.

        Uses the __iter__ property of the class to iterate over the geometries.

        Returns
        -------
        list
            List of the coordinates of each geometry in the collection
        """
        return [geom.to_coordinates() for geom in self]

    def _add_geometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.

        This should not directly be called by a Geometry:
        - A Geometry which inherits from `GeometryCollectionBase` has
            a specialized method. For example, `MultiPoint` has `add_point`.
        - A `GeometryCollection` has `add_geometry`.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        clone = lib.sfcgal_geometry_clone(geometry._geom)
        lib.sfcgal_geometry_collection_add_geometry(self._geom, clone)

    @cond_icontract(lambda self, n: n >= 0 and n < len(self), "require")
    def _set_geometry_n(self, geometry: Geometry, n: int) -> None:
        """Set the nth geometry of the collection.

        This should not directly be called by a Geometry:
        - A Geometry which inherits from `GeometryCollectionBase` has
            a specialized method. For example, `MultiPoint` has `set_point_n`.
        - A `GeometryCollection` has `set_geometry_n`.

        Parameters
        ----------
        geometry: Geometry
            The geometry to set.
        n : int
            Index of the geometry to set.
        """
        clone = lib.sfcgal_geometry_clone(geometry._geom)
        lib.sfcgal_geometry_collection_set_geometry_n(self._geom, clone, n)


class GeometryCollection(GeometryCollectionBase):
    def __init__(self):
        self._geom = lib.sfcgal_geometry_collection_create()

    def add_geometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        self._add_geometry(geometry)

    @deprecated("addGeometry() is deprecated. Use add_geometry() instead.")
    def addGeometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.
        This function is deprecated. Use add_geometry instead.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        self.add_geometry(geometry)

    def set_geometry_n(self, geometry: Geometry, n: int) -> None:
        """Set the nth geometry of the collection.

        Parameters
        ----------
        geometry: Geometry
            The geometry to set.
        n : int
            Index of the geometry to set.
        """
        self._set_geometry_n(geometry, n)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeometryCollection):
            return False
        return all(
            isinstance(other_geom, type(geom)) and geom == other_geom
            for geom, other_geom in zip(self, other)
        )

    def from_coordinates(self):
        """Instantiates a Point starting from a list of coordinates.

        Raises
        ------
        NotImplementedError
            This method is not supported (yet?). That's sounds too hard to infer the
            geometry type from a random coordinates structure.

        """
        raise NotImplementedError(
            "The 'from_coordinates' method is not implemented for GeometryCollection."
        )

    def to_dict(self) -> dict:
        """Generates a geojson-like dict representation of the GeometryCollection.

        This case differs from the general case, as the dictionary contains 'type' and
        'geometries' keys instead of 'type' and 'coordinates'. The 'geometries' key
        refers to the list of the dictionary representations of the geometries that
        belong the collection.

        Returns
        -------
        dict
            Geojson-like representation of the geometry collection

        """
        return {"type": self.geom_type, "geometries": [geom.to_dict() for geom in self]}

    @classmethod
    def from_dict(cls, geojson_data: dict) -> GeometryCollection:
        """Instantiates a GeometryCollection starting from a geojson-like dictionnary.

        The dictionary must contain 'type' and 'geometries' keys; the 'type' value
        should be 'GeometryCollection'. The 'geometries' values should be a list of
        valid geojson-like dictionaries that represents the geometries within the
        collection.

        Parameters
        ----------
        geojson_data : dict
            Description of the collection, in a geojson-like format

        Returns
        -------
        GeometryCollection
            An instance of GeometryCollection
        """
        # Lazy import that avoids circular imports between this module and the registry
        # module
        from .registry import geom_type_to_cls, geom_types

        if geojson_data.get("type") is None:
            raise KeyError("There is no 'type' key in the provided data.")
        if geojson_data["type"] != "GeometryCollection":
            raise ValueError(
                f"The provided 'type' ({geojson_data['type']}) "
                "should be 'GeometryCollection'."
            )
        if geojson_data.get("geometries") is None:
            raise KeyError("There is no 'geometries' key in the provided data.")
        collection = lib.sfcgal_geometry_collection_create()
        for geojson_geometry in geojson_data["geometries"]:
            geom_type = geojson_geometry["type"]
            geometry_cls = geom_type_to_cls[geom_types[geom_type]]
            geometry = geometry_cls.sfcgal_geom_from_coordinates(  # type: ignore
                geojson_geometry["coordinates"]
            )
            lib.sfcgal_geometry_collection_add_geometry(collection, geometry)
        return cast(
            GeometryCollection, GeometryCollection.from_sfcgal_geometry(collection))


class MultiPoint(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiPoint with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiPoint coordinates.
            If coords is empty, an empty MultiPoint is created.

        Returns
        -------
        MultiPoint
            A MultiPoint with coordinates coords

        """
        self._geom = MultiPoint.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiPoint starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiPoint coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiPoint

        """
        multipoint = lib.sfcgal_multi_point_create()
        for coords in coordinates:
            point = Point.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_geometry_collection_add_geometry(multipoint, point)
        return multipoint

    @cond_icontract(lambda self, point: point.geom_type == "Point", "require")
    def add_point(self, point: Point) -> None:
        """Add a point to the multipoint.

        Parameters
        ----------
        point: Point
            The point to add.
        """
        self._add_geometry(point)

    @cond_icontract(lambda self, point: point.geom_type == "Point", "require")
    def set_point_n(self, point: Point, n: int) -> None:
        """Set the nth point of the multipoint.

        Parameters
        ----------
        point: Point
            The point to set.
        n : int
            Index of the geometry to set.
        """
        self._set_geometry_n(point, n)


class MultiLineString(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiLineString with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiLineString coordinates.
            If coords is empty, an empty MultiLineString is created.

        Returns
        -------
        MultiLineString
            A MultiLineString with coordinates coords

        """
        self._geom = MultiLineString.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: Tuple, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL MultiLineString starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiLineString coordinates.
        close : bool
            If True, the linestrings are built as closed even if their coordinates are
            not, i.e. their first point is replicated at the last position.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiLineString

        """
        multilinestring = lib.sfcgal_multi_linestring_create()
        for coords in coordinates:
            linestring = LineString.sfcgal_geom_from_coordinates(coords, close=close)
            lib.sfcgal_geometry_collection_add_geometry(multilinestring, linestring)
        return multilinestring

    @cond_icontract(
        lambda self, linestring: linestring.geom_type == "LineString", "require")
    def add_linestring(self, linestring: LineString) -> None:
        """Add a linestring to the multilinestring.

        Parameters
        ----------
        linestring: LineString
            The linestring to add.
        """
        self._add_geometry(linestring)

    @cond_icontract(
        lambda self, linestring: linestring.geom_type == "LineString", "require")
    def set_linestring_n(self, linestring: LineString, n: int) -> None:
        """Set the nth geometry of the multilinestring.

        Parameters
        ----------
        linestring: LineString
            The linestring to set.
        n : int
            Index of the geometry to set.
        """
        self._set_geometry_n(linestring, n)


class MultiPolygon(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiPolygon with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiPolygon coordinates.
            If coords is empty, an empty MultiPolygon is created.

        Returns
        -------
        MultiPolygon
            A MultiPolygon with coordinates coords

        """
        self._geom = MultiPolygon.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiPolygon starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiPolygon coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiPolygon

        """
        multipolygon = lib.sfcgal_multi_polygon_create()
        if coordinates:
            for coords in coordinates:
                polygon = Polygon.sfcgal_geom_from_coordinates(coords)
                lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
        return multipolygon

    @cond_icontract(
        lambda self, polygon: polygon.geom_type == "Polygon", "require")
    def add_polygon(self, polygon: Polygon) -> None:
        """Add a polygon to the multipolygon.

        Parameters
        ----------
        polygon: Polygon
            The polygon to add.
        """
        self._add_geometry(polygon)

    @cond_icontract(lambda self, polygon: polygon.geom_type == "Polygon", "require")
    def set_polygon_n(self, polygon: Polygon, n: int) -> None:
        """Set the nth polygon of the multipolygon.

        Parameters
        ----------
        polygon: Polygon
            The polygon to set.
        n : int
            Index of the geometry to set.
        """
        self._set_geometry_n(polygon, n)


class MultiSolid(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiSolid with the given coordinates.

        Parameters
        ----------
        coords : tuples, optional
            A tuple where each element is the coordinates of a solid
            If coords is empty, an empty MultiSolid is created.

        """
        self._geom = MultiSolid.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiSolid starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiSolid coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiSolid

        """
        multisolid = lib.sfcgal_multi_solid_create()
        if coordinates:
            for coords in coordinates:
                solid = Solid.sfcgal_geom_from_coordinates(coords)
                lib.sfcgal_geometry_collection_add_geometry(multisolid, solid)
        return multisolid

    @cond_icontract(
        lambda self, solid: solid.geom_type == "Solid", "require")
    def add_solid(self, solid: Solid) -> None:
        """Add a solid to the multisolid.

        Parameters
        ----------
        solid: Solid
            The sold to add.
        """
        self._add_geometry(solid)

    @cond_icontract(lambda self, solid: solid.geom_type == "Solid", "require")
    def set_solid_n(self, solid: Solid, n: int) -> None:
        """Set the nth solid of the multisolid.

        Parameters
        ----------
        solid: Solid
            The solid to set.
        n : int
            Index of the geometry to set.
        """
        self._set_geometry_n(solid, n)
