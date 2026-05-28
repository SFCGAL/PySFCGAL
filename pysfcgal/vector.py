from dataclasses import dataclass


@dataclass(frozen=True)
class Vector3D:
    """3D Vector"""
    x: float
    y: float
    z: float


UNIT_X = Vector3D(1., 0., 0.)
UNIT_Y = Vector3D(0., 1., 0.)
UNIT_Z = Vector3D(0., 0., 1.)
