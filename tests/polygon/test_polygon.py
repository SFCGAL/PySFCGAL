import pytest

from pysfcgal.sfcgal import GeometryCollection, LineString, Point, Polygon


@pytest.fixture
def point_in_poly():
    yield Point(2., 3.)


@pytest.fixture
def polygon1(big_ring_ccw):
    yield Polygon(big_ring_ccw)


@pytest.fixture
def polygon2(ring_around_0_ccw):
    yield Polygon(ring_around_0_ccw)


@pytest.fixture
def polygon_with_hole(big_ring_ccw, small_ring_23_cw, small_ring_56_cw):
    yield Polygon(
        exterior=big_ring_ccw,
        interiors=[small_ring_23_cw, small_ring_56_cw]
    )


@pytest.fixture
def polygon_with_hole_unclosed(big_ring_ccw, small_ring_23_cw, small_ring_56_cw):
    yield Polygon(
        exterior=big_ring_ccw[:-1],
        interiors=[small_ring_23_cw[:-1], small_ring_56_cw[:-1]]
    )


@pytest.fixture
def vertical_polygon(vertical_ring):
    yield Polygon(exterior=vertical_ring)


@pytest.fixture
def linestring1_ccw(big_ring_ccw):
    yield LineString(big_ring_ccw)


@pytest.fixture
def linestring2_ccw(small_ring_23_ccw):
    yield LineString(small_ring_23_ccw)


@pytest.fixture
def linestring2_cw(small_ring_23_cw):
    yield LineString(small_ring_23_cw)


@pytest.fixture
def linestring3_cw(small_ring_56_cw):
    yield LineString(small_ring_56_cw)


def test_polygon_rings(
        polygon_with_hole, linestring1_ccw, linestring2_cw, linestring3_cw):
    # exterior ring
    assert polygon_with_hole.exterior == linestring1_ccw
    # interior rings
    assert polygon_with_hole.n_interiors == 2
    assert polygon_with_hole.interiors == [linestring2_cw, linestring3_cw]
    assert polygon_with_hole.rings == [linestring1_ccw, linestring2_cw, linestring3_cw]

    assert polygon_with_hole.is_valid()


def test_polygon_iteration(
        polygon_with_hole, linestring1_ccw, linestring2_cw, linestring3_cw):
    lines = [linestring1_ccw, linestring2_cw, linestring3_cw]
    for line, ring in zip(lines, polygon_with_hole):
        assert line == ring


def test_polygon_indexing(
        polygon_with_hole, linestring1_ccw, linestring2_cw, linestring3_cw):
    assert polygon_with_hole[0] == linestring1_ccw
    assert polygon_with_hole[1] == linestring2_cw
    assert polygon_with_hole[-1] == linestring3_cw
    assert polygon_with_hole[:] == [linestring1_ccw, linestring2_cw, linestring3_cw]
    assert polygon_with_hole[-1:-3:-1] == [linestring3_cw, linestring2_cw]


def test_polygon_equality(polygon_with_hole, polygon1, polygon_with_hole_unclosed):
    assert polygon_with_hole == polygon_with_hole_unclosed
    assert polygon_with_hole != polygon1


def test_polygon_to_coordinates(polygon1, big_ring_ccw):
    assert polygon1.to_coordinates() == [big_ring_ccw]
    cloned_polygon = Polygon(*polygon1.to_coordinates())
    assert cloned_polygon == polygon1
    other_polygon = Polygon.from_coordinates(polygon1.to_coordinates())
    assert other_polygon == polygon1


def test_polygon_to_dict(polygon1):
    polygon_data = polygon1.to_dict()
    other_polygon = Polygon.from_dict(polygon_data)
    assert other_polygon == polygon1


def test_point_in_polygon(point_in_poly, polygon1, polygon2):
    """Tests the intersection between a point and a polygon"""
    point = Point(2, 3)
    assert polygon1.intersects(point)
    assert point.intersects(polygon1)
    assert not polygon2.intersects(point)
    assert not point.intersects(polygon2)
    result = point.intersection(polygon1)
    assert isinstance(result, Point)
    assert not result.is_empty
    assert result.x == point.x
    assert result.y == point.y
    result = point.intersection(polygon2)
    assert isinstance(result, GeometryCollection)
    assert result.is_empty


def test_intersection_polygon_polygon(polygon1, polygon2):
    """Tests the intersection between two polygons"""
    assert polygon1.intersects(polygon2)
    assert polygon2.intersects(polygon1)
    polygon3 = polygon1.intersection(polygon2)
    assert polygon3.area == 1.0
    # TODO: check coordinates


def test_translate_2d(polygon1, big_ring_ccw):
    dx = 10.
    dy = 20.
    translated_polygon = polygon1.translate_2d(dx, dy)
    expected_ring_coordinates = [(x + dx, y + dy)
                                 for x, y in big_ring_ccw]
    assert translated_polygon.to_coordinates() == [expected_ring_coordinates]
    reverted_polygon = translated_polygon.translate_2d(-dx, -dy)
    assert polygon1.to_coordinates() == reverted_polygon.to_coordinates()


def test_translate_3d(polygon1, big_ring_ccw):
    dx = 10.
    dy = 20.
    dz = 30.
    translated_polygon = polygon1.translate_3d(dx, dy, dz)
    expected_ring_coordinates = [(x + dx, y + dy, dz)
                                 for x, y in big_ring_ccw]
    assert translated_polygon.to_coordinates() == [expected_ring_coordinates]
    # Apply a 2D-translation to a 3D geometry makes a 2D geometry
    reverted_polygon = translated_polygon.translate_2d(-dx, -dy)
    assert polygon1.to_coordinates() == reverted_polygon.to_coordinates()
    # Apply a 3D-translation to a 2D geometry makes a 3D geometry
    retranslated_polygon = reverted_polygon.translate_3d(dx, dy, dz)
    assert translated_polygon.to_coordinates() == retranslated_polygon.to_coordinates()


def test_vtk(tmp_test_dir, polygon1):
    vtk = polygon1.to_vtk()
    vtk_filepath = tmp_test_dir / "poly.vtk"
    polygon1.write_vtk(str(vtk_filepath))
    with open(vtk_filepath) as vtk_fobj:
        for vtk_str_line, vtk_file_line in zip(vtk.split("\n"), vtk_fobj):
            assert vtk_str_line + "\n" == vtk_file_line


def test_obj(tmp_test_dir, polygon1):
    obj = polygon1.to_obj()
    obj_filepath = tmp_test_dir / "poly.obj"
    polygon1.write_obj(str(obj_filepath))
    with open(obj_filepath) as obj_fobj:
        for obj_str_line, obj_file_line in zip(obj.split("\n"), obj_fobj):
            assert obj_str_line + "\n" == obj_file_line


def test_set_exterior_ring(polygon1, linestring1_ccw, linestring2_ccw):
    assert polygon1.n_interiors == 0
    assert polygon1.rings == [linestring1_ccw]
    assert polygon1.is_valid()

    polygon1.set_exterior_ring(linestring2_ccw)
    assert polygon1.n_interiors == 0
    assert polygon1.rings == [linestring2_ccw]
    assert polygon1.is_valid()


def test_add_interior_ring(polygon1, linestring1_ccw, linestring2_cw):
    assert polygon1.n_interiors == 0
    assert polygon1.rings == [linestring1_ccw]
    assert polygon1.is_valid()

    polygon1.add_interior_ring(linestring2_cw)
    assert polygon1.n_interiors == 1
    assert polygon1.interiors == [linestring2_cw]
    assert polygon1.rings == [linestring1_ccw, linestring2_cw]
    assert polygon1.is_valid()


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_centroid(polygon1: Polygon, compute_2d_area: bool) -> None:
    assert polygon1.centroid(compute_2d_area) == Point(5, 5)


@pytest.mark.parametrize("compute_2d_area", [True, False])
def test_centroid_vertical(vertical_polygon: Polygon, compute_2d_area: bool) -> None:
    assert (vertical_polygon.centroid(compute_2d_area) is not None) ^ compute_2d_area
