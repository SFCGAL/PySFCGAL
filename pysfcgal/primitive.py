"""The `primitive` contains the logic to handle primitives.

Primtives are box, cone, cube, cylinder, sphere, torus.
"""

from __future__ import annotations

import json
import sys
from enum import Enum, IntEnum
from typing import Any, Callable, Optional, TypeVar

from ._sfcgal import ffi, lib
from .geometry import PolyhedralSurface

parameterVal = TypeVar("parameterVal", int, float)


class PrimitiveType(IntEnum):
    """
    Enumeration of primitive 3D geometry types.

    Attributes
    ----------
    label : str
        A descriptive name associated with the primitive.
    """
    label: str

    BOX = lib.SFCGAL_TYPE_BOX, "Box"
    CONE = lib.SFCGAL_TYPE_CONE, "Cone"
    CUBE = lib.SFCGAL_TYPE_CUBE, "Cube"
    CYLINDER = lib.SFCGAL_TYPE_CYLINDER, "Cylinder"
    SPHERE = lib.SFCGAL_TYPE_SPHERE, "Sphere"
    TORUS = lib.SFCGAL_TYPE_TORUS, "Torus"

    def __new__(cls: PrimitiveType, value: int, label: str) -> PrimitiveType:
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        """
        Returns a readable string
        """
        return f"{self.label} ({self.value})"


class ParameterType(Enum):
    """
    Enumeration of parameter types used for primitive attributes.

    Attributes
    ----------
    getter : Callable[..., Any]
        Function used to retrieve the parameter value.
    setter : Callable[..., Any]
        Function used to set the parameter value.
    """
    getter: Callable[..., Any]
    setter: Callable[..., Any]

    DOUBLE = (
        "double",
        lib.sfcgal_primitive_parameter_double,
        lib.sfcgal_primitive_set_parameter_double,
    )
    INT = (
        "int",
        lib.sfcgal_primitive_parameter_int,
        lib.sfcgal_primitive_set_parameter_int,
    )

    def __new__(
            cls: ParameterType, value: str, getter: Callable[..., Any],
            setter: Callable[..., Any]) -> ParameterType:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.getter = getter
        obj.setter = setter
        return obj

    def __str__(self) -> str:
        """
        Returns a readable string
        """
        return self.value


class Primitive:
    """
    This class provides a Pythonic interface to create, manipulate, and
    query geometric primitives.
    It supports dynamic parameter access using dictionary-style indexing
    as well as generated properties.

    Examples
    --------
    >>> sphere = Primitive(PrimitiveType.SPHERE)
    >>> sphere["radius"] = 5.0
    >>> sphere["radius"]
    5.0
    >>> sphere.radius = 3.2
    >>> sphere.radius
    3.2

    >>> cube = Cube(size=2.0)
    >>> cube.size
    2.0
    >>> cube["size"]
    2.0
    """
    __primitive: ffi.CData
    __type: PrimitiveType
    _params_cache: dict[PrimitiveType, dict[str, ParameterType]] = {}

    __slots__ = ("__parameters", "__primitive", "__type")

    def __init__(self, primitive_type: PrimitiveType):
        """Initialize a Primitive by its type.

        Parameters
        ----------
        primitive_type : PrimitiveType
            The primitive type.
        """
        self.__type = primitive_type
        self.__primitive = lib.sfcgal_primitive_create(primitive_type.value)
        self.__parameters = self._populate_parameters(primitive_type)

    def __del__(self):
        lib.sfcgal_primitive_delete(self.__primitive)

    @property
    def type_(self) -> PrimitiveType:
        """
        Return the type of the primitive.

        Returns
        -------
        PrimitiveType
            The enum value representing the primitive's type.
        """
        return self.__type

    @property
    def parameters(self) -> list[dict[str, str]]:
        """
        Return the parameters available for this primitive.

        Returns
        -------
        dict[str, ParameterType]
            A mapping of parameter names to their corresponding ParameterType.
        """
        return self.__parameters

    def __getitem__(self, name: str) -> parameterVal:
        """
        Retrieve the value of a primitive parameter by name.

        Parameters
        ----------
        name : str
           The name of the parameter.

        Returns
        -------
        int | double
            The parameter value.

        Raises
        ------
        KeyError
            If the parameter does not exist.
        """
        param_type = self.__parameters.get(name)
        if not param_type:
            raise KeyError(f"'{type(self).__name__}' has no attribute '{name}'")

        return param_type.getter(self.__primitive, name.encode())

    def __setitem__(self, name: str, value: parameterVal) -> None:
        """
        Set the value of a primitive parameter by name.

        Parameters
        ----------
        name : str
            The name of the parameter.
        value : Any
            The value to assign to the parameter.

        Raises
        ------
        KeyError
            If the parameter does not exist.
        """
        param_type = self.__parameters.get(name)
        if not param_type:
            raise KeyError(f"'{type(self).__name__}' has no attribute '{name}'")
        param_type.setter(self.__primitive, name.encode(), value)

    def __eq__(self, other: object) -> bool:
        """Check equality between two Primitive instances.

        Two primitives are equal if they have the same type and their
        parameters are equal.

        Parameters
        ----------
        other : object
            The object to compare with.

        Returns
        -------
        bool
            True if both points have the same coordinates, False otherwise.
        """
        if not isinstance(other, Primitive):
            return False

        return bool(lib.sfcgal_primitive_is_almost_equals(
            self.__primitive, other.__primitive, 0.0))

    def __repr__(self) -> str:
        """
        Return a string representation of the primitive.
        """
        params = ", ".join(f"{n}={self[n]}" for n in self.__parameters)
        return f"{self.__type.label}({params})"

    @staticmethod
    def _populate_parameters(primitive_type: PrimitiveType) -> dict[str, ParameterType]:
        """
        Retrieve and cache parameter definitions for a given primitive type.

        This method queries the SFCGAL C library to obtain parameter
        metadata, converts it into a Python mapping, and caches the
        result for future use.

        This method is intended for internal use only.

        Parameters
        ----------
        primitive_type : PrimitiveType
            The primitive type to inspect.

        Returns
        -------
        dict[str, ParameterType]
            A mapping of parameter names to their corresponding ParameterType.
        """
        if primitive_type not in Primitive._params_cache:
            tmp_ffi = lib.sfcgal_primitive_create(primitive_type.value)
            buffer = ffi.new("char**")
            length = ffi.new("size_t*")
            json_params = []
            try:
                lib.sfcgal_primitive_parameters(tmp_ffi, buffer, length)
                json_params = ffi.string(buffer[0], length[0]).decode("utf-8")
            finally:
                # we're responsible for free'ing the memory
                lib.sfcgal_primitive_delete(tmp_ffi)
                if not buffer[0] == ffi.NULL:
                    lib.free(buffer[0])

            params = {}
            if json_params:
                for parameter in json.loads(json_params):
                    params[parameter["name"]] = ParameterType(parameter["type"])

            Primitive._params_cache[primitive_type] = params

        return Primitive._params_cache[primitive_type]

    @staticmethod
    def _primitive_factory(primitive_type: PrimitiveType):
        """
        Dynamically create a specialized Primitive subclass for a given type.

        The generated class:
        - Initializes a primitive of the given type
        - Accepts parameter values as keyword arguments
        - Exposes parameters as Python properties

        This method is intended for internal use only.

        Parameters
        ----------
        primitive_type : PrimitiveType
            The type of primitive to generate.

        Returns
        -------
        type
           A dynamically created subclass of Primitive.
        """
        params = Primitive._populate_parameters(primitive_type)

        class Class(Primitive):
            __slots__ = ()

            def __init__(self, **kwargs):
                super().__init__(primitive_type)

                for name, value in kwargs.items():
                    self[name] = value

        Class.__name__ = primitive_type.label
        Class.__qualname__ = primitive_type.label

        for param_name in params:
            def getter(self, n=param_name):
                return self[n]

            def setter(self, value, n=param_name):
                self[n] = value

            setattr(Class, param_name, property(getter, setter))

        return Class

    @staticmethod
    def from_sfcgal_primitive(prim: ffi.CData) -> Optional[Primitive]:
        """Wrap the SFCGAL primitive passed as a parameter in a new primitive instance.

        This method allows to build a new Python object from a SFCGAL primitive (which
        is basically a C pointer).

        Parameters
        ----------
        prim : _cffi_backend._CDatabase
            SFCGAL primitive that will be used as an attribute in the new primitive
            instance

        Returns
        -------
        Primitive
            A Primitive instance built from the SFCGAL primitive parameter.

        """
        type_ = lib.sfcgal_primitive_type_id(prim)
        if type_ == lib.SFCGAL_TYPE_INVALID:
            return None

        prim_type = PrimitiveType(type_)
        cls = globals()[prim_type.label]
        primitive: Primitive = object.__new__(cls)
        primitive._Primitive__primitive = prim
        primitive._Primitive__type = prim_type
        primitive._Primitive__parameters = Primitive._populate_parameters(prim_type)
        return primitive

    def to_polyhedral_surface(self) -> PolyhedralSurface:
        """
        Convert the primitive to a polyhedral surface representation.

        Returns
        -------
        PolyhedralSurface
            The converted polyhedral surface object.
        """
        phs = lib.sfcgal_primitive_as_polyhedral_surface(self.__primitive)
        return PolyhedralSurface.from_sfcgal_geometry(phs)

    def area(self, with_discretization: bool = False) -> float:
        """
        Compute the surface area of the primitive.

        Parameters
        ----------
        with_discretization : bool, optional
            Whether to approximate curved surfaces via discretization.

        Returns
        -------
        float
            The computed surface area.
        """
        return lib.sfcgal_primitive_area(self.__primitive, with_discretization)

    def volume(self, with_discretization: bool = False) -> float:
        """
        Compute the volume of the primitive.

        Parameters
        ----------
        with_discretization : bool, optional
            Whether to approximate curved surfaces via discretization.

        Returns
        -------
        float
            The computed volume.
        """
        return lib.sfcgal_primitive_volume(self.__primitive, with_discretization)

    def wrap(self) -> Optional[Primitive]:
        """Wrap the SFCGAL primitive attribute of the current instance
        in a new primitive instance. This method produces a deep copy
        of the primitive instance.

        Returns
        -------
        Primitive
            A cloned Primitive of the current instance

        """
        cloned_prim = lib.sfcgal_primitive_clone(self.__primitive)
        return Primitive.from_sfcgal_primitive(cloned_prim)


# Generate the different Primitives and store them in the module
_module = sys.modules[__name__]
for primitive_type in PrimitiveType:
    _cls = Primitive._primitive_factory(primitive_type)
    setattr(_module, primitive_type.label, _cls)
