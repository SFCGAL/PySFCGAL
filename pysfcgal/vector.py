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
        squared_norm = self.x * self.x + self.y * self.y + self.z * self.z
        if math.isclose(squared_norm, 0.0) or math.isclose(squared_norm, 1.0):
            return

        norm = math.sqrt(squared_norm)
        self.x /= norm
        self.y /= norm
        self.z /= norm


UNIT_X = Vector3D(1., 0., 0.)
UNIT_Y = Vector3D(0., 1., 0.)
UNIT_Z = Vector3D(0., 0., 1.)
