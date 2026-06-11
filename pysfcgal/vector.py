import math
from dataclasses import dataclass


@dataclass(slots=True)
class Vector3D:
    """3D Vector"""
    x: float
    y: float
    z: float

    def normalize(self):
        """
        Normalizes the current vector in place.

        Nothing happens if this vector is a null vector or the length of
        the vector is very close to 1.
        """
        len2 = self.x * self.x + self.y * self.y + self.z * self.z
        if math.isclose(len2, 0.0) or math.isclose(len2, 1.0):
            return

        len = math.sqrt(len2)
        self.x /= len
        self.y /= len
        self.z /= len


UNIT_X = Vector3D(1., 0., 0.)
UNIT_Y = Vector3D(0., 1., 0.)
UNIT_Z = Vector3D(0., 0., 1.)
