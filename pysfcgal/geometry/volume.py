"""3D volume geometries.

This module focuses particularly on Solid, which is not a Simple Feature geometry.
However it is mentionned in the norm as a particular case of PolyhedralSurface (when 3D
surfaces are closed).

There is a strong bidirectional relationship between Solid and PolyhedralSurface, that
leads to a bunch of lazy imports to handle things.

"""

from __future__ import annotations

import typing
from typing import Tuple, Union

if typing.TYPE_CHECKING:
    from .surface import PolyhedralSurface

from .._contracts import cond_icontract
from .._sfcgal import ffi, lib
from .geometry import Geometry

__all__ = ["Solid"]


class Solid(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize the Solid with the given coordinates.

        Parameters
        ----------
        coords : list of list of tuples, optional
            A tuple where the first element is the exterior shell coordinates, and the
            subsequent elements are the interior shell coordinates.
            If coords is empty, an empty Solid is created.

        """
        self._geom = Solid.sfcgal_geom_from_coordinates(coords)

    def __iter__(self):
        """Iterate over the shells of the solid.

        Yields
        ------
        Geometry
            Each shell of the solid as a Geometry object.
        """
        for n in range(self.n_shells):
            yield self.__get_shell_n(n)

    def __getitem__(self, key):
        """Get a shell (or several) within a solid, identified through an index or a
        slice. The first shell is always the exterior shell, the next ones are the
        interior shells (optional).

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the shell(s) to recover.

        Returns
        -------
        PolyhedralSurface or list of PolyhedralSurface
            The shell(s) at the specified index or slice.
        """
        length = self.n_shells
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_shell_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_shell_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Two Solids are equal if their shells (exterior and interior) are equal.

        Parameters
        ----------
        other : Solid
            The other solid to compare.

        Returns
        -------
        bool
            True if both solids contain the same shells, False otherwise.
        """
        if not isinstance(other, Solid):
            return False
        if self.n_shells != other.n_shells:
            return False
        return all(phs == other_phs for phs, other_phs in zip(self, other))

    def __len__(self):
        """Return the number of shells in the solid.

        Returns
        -------
        int
            The number of shells contained within the solid.
        """
        return lib.sfcgal_solid_num_shells(self._geom)

    @property
    def n_shells(self):
        """Get the number of shells in the solid.

        Returns
        -------
        int
            The number of shells contained within the solid.
        """
        return len(self)

    @property
    def shells(self):
        """Get the shells of the solid.

        Returns
        -------
        list of Geometry
            A list of shells as Geometry objects.
        """
        _shells = []
        for idx in range(self.n_shells):
            _shells.append(
                Geometry.from_sfcgal_geometry(
                    lib.sfcgal_solid_shell_n(self._geom, idx), owned=False, parent=self,
                )
            )
        return _shells

    def __get_shell_n(self, n):
        """Returns the n-th shell within the solid. This method is internal and makes
        the assumption that the index is valid for the geometry. The 0 index refers to
        the exterior shell.

        Parameters
        ----------
        n : int
            Index of the shell to recover.

        Returns
        -------
        PolyhedralSurface
            The shell at the specified index.
        """
        return self.shells[n]

    def to_polyhedralsurface(
            self, wrapped: bool = True) -> Union[PolyhedralSurface, ffi.CData]:
        """Convert the solid to a PolyhedralSurface.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the returned geometry in a Geometry object. Defaults to True.

        Returns
        -------
        PolyhedralSurface
            The corresponding PolyhedralSurface representation of the solid.
        """
        phs_geom = lib.sfcgal_polyhedral_surface_create()

        for shell in self.shells:
            num_geoms = lib.sfcgal_polyhedral_surface_num_patches(shell._geom)
            for geom_idx in range(num_geoms):
                polygon = lib.sfcgal_polyhedral_surface_patch_n(shell._geom, geom_idx)
                lib.sfcgal_polyhedral_surface_add_patch(
                    phs_geom, lib.sfcgal_geometry_clone(polygon)
                )
        return Geometry.from_sfcgal_geometry(phs_geom) if wrapped else phs_geom

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: Tuple, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL Solid starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            A tuple of coordinate tuples representing the solid's shells.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Solid.
        """
        from .surface import PolyhedralSurface

        solid = lib.sfcgal_solid_create()
        if coordinates:
            polyhedralsurface = PolyhedralSurface.sfcgal_geom_from_coordinates(
                coordinates[0]
            )
            solid = lib.sfcgal_solid_create_from_exterior_shell(polyhedralsurface)
            for coords in coordinates[1:]:
                polyhedralsurface = PolyhedralSurface.sfcgal_geom_from_coordinates(
                    coords
                )
                lib.sfcgal_solid_add_interior_shell(solid, polyhedralsurface)
        return solid

    @cond_icontract(
        lambda self, shell: shell.geom_type == "PolyhedralSurface", "require")
    def set_exterior_shell(self, shell: PolyhedralSurface) -> None:
        """Sets the exterior of the solid.

        Parameters
        ----------
        shell : PolyhedralSurface
            The new exterior shell

        """
        shell_clone = lib.sfcgal_geometry_clone(shell._geom)
        lib.sfcgal_solid_set_exterior_shell(self._geom, shell_clone)

    @cond_icontract(
        lambda self, shell: shell.geom_type == "PolyhedralSurface", "require")
    def add_interior_shell(self, shell: PolyhedralSurface) -> None:
        """Adds an interior shell to the solid.

        Parameters
        ----------
        shell : PolyhedralSurface
            The interior shell to add

        """
        shell_clone = lib.sfcgal_geometry_clone(shell._geom)
        lib.sfcgal_solid_add_interior_shell(self._geom, shell_clone)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the Solid.

        Uses the __iter__ property of the Solid to iterate over shells.

        Returns
        -------
        list
            List of shells' coordinates.
        """
        return [shells.to_coordinates() for shells in self]
