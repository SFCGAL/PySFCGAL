from pathlib import Path

import pytest

from pysfcgal import Geometry
from tests.utils import (multilinestring_factory, multipoint_factory,
                         polyhedral_surface_factory, tin_factory)

# One has to overload the geometry factories defined in the utils module, as the OBJ
# format produces a reduced range of geometry types.
OBJ_GEOMETRY_FACTORIES = {
    "Point": multipoint_factory,
    "MultiPoint": multipoint_factory,
    "LineString": multilinestring_factory,
    "MultiLineString": multilinestring_factory,
    "Polygon": polyhedral_surface_factory,
    "MultiPolygon": polyhedral_surface_factory,
    "GeometryCollection": polyhedral_surface_factory,
    "Triangle": tin_factory,
    "TIN": tin_factory,
    "PolyhedralSurface": polyhedral_surface_factory,
    "Solid": polyhedral_surface_factory,
    "MultiSolid": polyhedral_surface_factory,
}


@pytest.mark.parametrize(
    "filename", ["bunny.obj", "teddy.obj", "teapot.obj", "cow-nonormals.obj"]
)
def test_read_obj(filename: str, fixture_dir: Path, tmp_test_dir: Path) -> None:
    """Read a complex OBJ file.

    Write it to a temporary file and re-read it. It should be comparable with the
    initial data.

    """
    geom = Geometry.read_obj(str(fixture_dir / filename))
    assert geom.geom_type == "TriangulatedSurface"
    tmp_filepath = str(tmp_test_dir / filename)
    geom.write_obj(tmp_filepath)
    copied_geom = Geometry.read_obj(tmp_filepath)
    assert len(geom) == len(copied_geom)
    assert geom.geom_type == copied_geom.geom_type
    assert geom.n_edges == copied_geom.n_edges


@pytest.mark.parametrize(
    "geom_factory",
    OBJ_GEOMETRY_FACTORIES.values(),
    ids=OBJ_GEOMETRY_FACTORIES.keys()
)
def test_geom_to_obj(geom_factory):
    """Test the from_obj/to_obj methods.

    Reading OBJ files through SFCGAL generates 3D geometries with following types:

    - TIN if faces are triangular.
    - PolyhedralSurface if there are other types of faces.
    - MultiLineString if there are only lines and vertices.
    - MultiPoint if there are only points and vertices.

    """
    geom = geom_factory(1.0)
    geom_obj = geom.to_obj()
    other_geom = Geometry.from_obj(geom_obj)
    assert other_geom == geom
