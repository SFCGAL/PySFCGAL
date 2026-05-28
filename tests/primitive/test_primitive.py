import pytest

from pysfcgal import PolyhedralSurface, primitive
from pysfcgal.vector import Vector3D


@pytest.fixture
def identity() -> list[float]:
    yield [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]


# Factory to test a primitive:
#   - type
#   - object
#   - parameters with custom values
#   - expected area and volume with and without discretization
PRIMITIVES_FACTORY = [
    (
        primitive.PrimitiveType.BOX,
        primitive.Box,
        {"x_extent": 4.0, "y_extent": 5.0, "z_extent": 7.0},
        [(166.0, 140.0), (166.0, 140.0)],
    ),
    (
        primitive.PrimitiveType.CONE,
        primitive.Cone,
        {"bottom_radius": 4.0, "top_radius": 0.2, "height": 7, "num_radial": 32},
        [(154.879135, 122.651984), (155.485830, 123.443647)],
    ),
    (
        primitive.PrimitiveType.CUBE,
        primitive.Cube,
        {"size": 3.0},
        [(54.0, 27.0), (54.0, 27.0)],
    ),
    (
        primitive.PrimitiveType.CYLINDER,
        primitive.Cylinder,
        {"radius": 5.0, "height": 10.0, "num_radial": 32},
        [(471.238898, 785.398163), (471.238898, 785.398163)],
    ),
    (
        primitive.PrimitiveType.SPHERE,
        primitive.Sphere,
        {"radius": 8.0, "num_subdivisions": 2},
        [(804.247719, 2144.66058), (804.247719, 2144.66058)],
    ),
    (
        primitive.PrimitiveType.TORUS,
        primitive.Torus,
        {
            "main_radius": 14,
            "tube_radius": 7,
            "main_num_radial": 16,
            "tube_num_radial": 64
        },
        [(3868.884925, 13541.1), (3868.884925, 13541.1)],
    ),
]


@pytest.mark.parametrize(
    "primitive_type", [p[0] for p in PRIMITIVES_FACTORY])
def test_create_from_base_class(primitive_type):
    """
    Create primitives from the base class and check that its parameters
    can be retrieved and set
    """
    prim = primitive.Primitive(primitive_type)
    assert prim.type_ == primitive_type
    double_value = 5.2
    for param_name, param_type in prim.parameters.items():
        if param_type == primitive.ParameterType.DOUBLE:
            assert prim[param_name] != double_value
            prim[param_name] = double_value
            assert prim[param_name] == double_value
            double_value += 1.0
        elif param_type == primitive.ParameterType.INT:
            assert prim[param_name] != 4
            prim[param_name] = 4
            assert prim[param_name] == 4
        else:
            assert False


@pytest.mark.parametrize(
    "primitive_type,primitive_class,init_values,__", PRIMITIVES_FACTORY)
def test_create_primitives(primitive_type, primitive_class, init_values, __):
    """
    - Create primitives from the child class (Cube, Sphere, etc.) with
      default values
    - Create primitives from the child class (Cube, Sphere, etc.) with
      custom values
    - Check that the parameters can be retrieved and set
    - Check that setting an invalid parameter raises an error
    """
    prim = primitive_class()
    assert prim is not None
    assert prim.type_ == primitive_type
    for parameter in init_values.keys():
        assert hasattr(prim, parameter)
    with pytest.raises(AttributeError):
        prim.foo = 3
    prim_2 = primitive_class(**init_values)
    for name, value in init_values.items():
        assert prim_2[name] == value
    first_name, first_value = next(iter(init_values.items()))
    prim_3 = primitive_class(**{first_name: first_value})
    assert prim_3[first_name] == first_value


@pytest.mark.parametrize(
    "primitive_class", [p[1] for p in PRIMITIVES_FACTORY])
def test_to_polyhedral_surface(primitive_class):
    prim = primitive_class()
    phs = prim.to_polyhedral_surface()
    assert isinstance(phs, PolyhedralSurface)


@pytest.mark.parametrize(
    "primitive_type,primitive_class,init_values,area_volume", PRIMITIVES_FACTORY)
def test_area_volume(primitive_class, primitive_type, init_values, area_volume):
    prim = primitive_class(**init_values)
    for name, value in init_values.items():
        assert prim[name] == value

    # for area and volumes
    # check 2 cases: without discretization and with discretization
    for idx in range(2):
        area, volume = area_volume[idx]
        assert pytest.approx(prim.area(idx == 0), 1e-6) == area
        assert pytest.approx(prim.volume(idx == 0), 1e-6) == volume


@pytest.mark.parametrize(
    "primitive_class,init_values", [(p[1], p[2]) for p in PRIMITIVES_FACTORY])
def test_equality(primitive_class, init_values):
    prim = primitive_class(**init_values)
    other_prim = primitive_class(**init_values)
    assert prim == other_prim

    first_param = next(iter(init_values))
    prim[first_param] += 1
    assert prim != other_prim


@pytest.mark.parametrize(
    "primitive_class,init_values", [(p[1], p[2]) for p in PRIMITIVES_FACTORY])
def test_wrap(primitive_class, init_values):
    prim = primitive_class(**init_values)
    prim_wrap = prim.wrap()
    assert prim_wrap == prim

    first_param = next(iter(init_values))
    prim[first_param] += 1
    assert prim[first_param] != prim_wrap[first_param]


@pytest.mark.parametrize(
    "primitive_class,init_values", [(p[1], p[2]) for p in PRIMITIVES_FACTORY])
def test_translate(primitive_class, init_values, identity):
    prim = primitive_class(**init_values)
    assert prim.transformation == identity

    translated_prim = prim.translate(Vector3D(2, 3, 4))
    expected_translation = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        2, 3, 4, 1
    ]
    assert translated_prim.transformation != identity
    assert translated_prim.transformation == expected_translation
