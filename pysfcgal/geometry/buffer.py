"""Design the buffer types.

The buffer type describes the way a buffer is generated around a LineString (not
required in the Point case).

"""

from enum import IntEnum
from typing import Type

from .._sfcgal import lib


class BufferType(IntEnum):
    label: str

    SFCGAL_BUFFER3D_ROUND = lib.SFCGAL_BUFFER3D_ROUND, "Round"
    SFCGAL_BUFFER3D_CYLSPHERE = lib.SFCGAL_BUFFER3D_CYLSPHERE, "CylSphere"
    SFCGAL_BUFFER3D_FLAT = lib.SFCGAL_BUFFER3D_FLAT, "Flat"

    def __new__(cls: Type["BufferType"], value: int, label: str) -> "BufferType":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return f"{self.label} ({self.value})"
