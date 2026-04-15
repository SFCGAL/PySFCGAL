"""The `primitive` contains the logic to handle primitives.

Primtives are box, cone, cube, cylinder, sphere, torus.
"""

from __future__ import annotations

import json
import sys
from enum import Enum, IntEnum
from typing import Any, Callable, TypeVar

from ._sfcgal import ffi, lib
from .sfcgal import PolyhedralSurface

parameterVal = TypeVar("parameterVal", int, float, list[float])


class PrimitiveType(IntEnum):
    """
    Enumeration of primitive 3D geometry types.

    Attributes
    ----------
    label : str
        A descriptive name associated with the primitive.
    """
    label: str

    BOX = 0, "Box"
    CONE = 1, "Cone"
    CUBE = 2, "Cube"
    CYLINDER = 3, "Cylinder"
    SPHERE = 4, "Sphere"
    TORUS = 5, "Torus"

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
    POINT = (
        "point3",
        lib.sfcgal_primitive_parameter_point,
        lib.sfcgal_primitive_set_parameter_point,
    )
    VECTOR = (
        "vector3",
        lib.sfcgal_primitive_parameter_vector,
        lib.sfcgal_primitive_set_parameter_vector,
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
        Any
            The parameter value. For POINT and VECTOR types, a list of
            coordinates is returned. Otherwise, a scalar value is
            returned.

        Raises
        ------
        KeyError
            If the parameter does not exist.
        """
        param_type = self.__parameters.get(name)
        if not param_type:
            raise KeyError(f"'{type(self).__name__}' has no attribute '{name}'")

        ffi_value = param_type.getter(self.__primitive, name.encode())
        if param_type in [ParameterType.POINT, ParameterType.VECTOR]:
            value = list(ffi_value[0:3])
            lib.sfcgal_free_buffer(ffi_value)
            return value
        else:
            return ffi_value

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


# Generate the different Primitives and store them in the module
_module = sys.modules[__name__]
for primitive_type in PrimitiveType:
    _cls = Primitive._primitive_factory(primitive_type)
    setattr(_module, primitive_type.label, _cls)
