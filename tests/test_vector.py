import math

from pysfcgal.vector import Vector3D


def test_vector3d_normalize():
    null_vector = Vector3D(0.0, 0.0, 0.0)
    null_vector.normalize()
    assert null_vector == Vector3D(0.0, 0.0, 0.0)

    unit_vector = Vector3D(1, 0, 0)
    unit_vector.normalize()
    assert unit_vector == Vector3D(1, 0, 0)

    unit_vector = Vector3D(0, 1, 0)
    unit_vector.normalize()
    assert unit_vector == Vector3D(0, 1, 0)

    unit_vector = Vector3D(0, 0, 1)
    unit_vector.normalize()
    assert unit_vector == Vector3D(0, 0, 1)

    vector = Vector3D(3, 2, 1)
    vector.normalize()
    assert math.isclose(vector.x, 0.8017837257372732)
    assert math.isclose(vector.y, 0.5345224838248488)
    assert math.isclose(vector.z, 0.2672612419124244)
