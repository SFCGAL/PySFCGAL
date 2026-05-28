from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any, Callable, Optional, TypeVar

from ._sfcgal import ffi
from .geometry import Point, PolyhedralSurface
from .vector import Vector3D

parameterVal = TypeVar("parameterVal", int, float)


class PrimitiveType(IntEnum):

    label: str

    BOX = ...
    CONE = ...
    CUBE = ...
    CYLINDER = ...
    SPHERE = ...
    TORUS = ...

    def __new__(cls, value: int, label: str) -> PrimitiveType: ...
    def __str__(self) -> str: ...


class ParameterType(Enum):

    getter: Callable[..., Any]
    setter: Callable[..., Any]

    DOUBLE = ...
    INT = ...

    def __new__(
        cls,
        value: str,
        getter: Callable[..., Any],
        setter: Callable[..., Any],
    ) -> ParameterType: ...
    def __str__(self) -> str: ...


class Primitive:

    def __init__(
            self,
            primitive_type: PrimitiveType,
            center: Optional[Point] = None
    ) -> None: ...
    def __del__(self) -> None: ...

    @property
    def type_(self) -> PrimitiveType: ...
    @property
    def transformation(self) -> list[float]: ...
    @property
    def center(self) -> Point: ...
    @property
    def parameters(self) -> dict[str, ParameterType]: ...

    def __getitem__(self, name: str) -> int | float: ...
    def __setitem__(self, name: str, value: int | float) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...

    @staticmethod
    def _populate_parameters(
        primitive_type: PrimitiveType,
    ) -> dict[str, ParameterType]: ...

    @staticmethod
    def _primitive_factory(primitive_type: PrimitiveType) -> type[Primitive]: ...

    @staticmethod
    def from_sfcgal_primitive(prim: ffi.CData) -> Optional[type[Primitive]]: ...

    def translate(self, offset: Vector3D) -> Optional[type[Primitive]]: ...
    def to_polyhedral_surface(self) -> PolyhedralSurface: ...
    def area(self, with_discretization: bool = False) -> float: ...
    def volume(self, with_discretization: bool = False) -> float: ...
    def wrap(self) -> Optional[type[Primitive]]: ...


class Box(Primitive):
    x_extent: float
    y_extent: float
    z_extent: float

    def __init__(
            self,
            *,
            x_extent: float = ...,
            y_extent: float = ...,
            z_extent: float = ...,
            center: Optional[Point] = None
    ) -> None: ...


class Cone(Primitive):
    bottom_radius: float
    top_radius: float
    height: float
    num_radial: int

    def __init__(
            self,
            *,
            bottom_radius: float = ...,
            top_radius: float = ...,
            height: float = ...,
            num_radial: int = ...,
            center: Optional[Point] = None
    ) -> None: ...


class Cube(Primitive):
    size: float

    def __init__(
            self,
            *,
            size: float = ...,
            center: Optional[Point] = None
    ) -> None: ...


class Cylinder(Primitive):
    radius: float
    height: float
    num_radial: int

    def __init__(
            self,
            *,
            radius: float = ...,
            height: float = ...,
            num_radial: int = ...,
            center: Optional[Point] = None
    ) -> None: ...


class Sphere(Primitive):
    radius: float
    num_subdivisions: int

    def __init__(
            self,
            *,
            radius: float = ...,
            num_subdivisions: int = ...,
            center: Optional[Point] = None
    ) -> None: ...


class Torus(Primitive):
    main_radius: float
    tube_radius: float
    main_num_radial: int
    tube_num_radial: int

    def __init__(
            self,
            *,
            main_radius: float = ...,
            tube_radius: float = ...,
            main_num_radial: int = ...,
            tube_num_radial: int = ...,
            center: Optional[Point] = None
    ) -> None: ...
