"""Design the buffer types.

The buffer type describes the way a buffer is generated around a LineString (not
required in the Point case).

"""

from enum import IntEnum
from typing import Type


class BufferType(IntEnum):
    label: str

    SFCGAL_BUFFER3D_ROUND = 0, "Round"
    SFCGAL_BUFFER3D_CYLSPHERE = 1, "CylSphere"
    SFCGAL_BUFFER3D_FLAT = 2, "Flat"

    def __new__(cls: Type["BufferType"], value: int, label: str) -> "BufferType":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return f"{self.label} ({self.value})"
