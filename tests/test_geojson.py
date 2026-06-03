import json
from pathlib import Path

import pytest

from pysfcgal import Geometry, Point, Polygon
from tests.utils import GEOMETRY_FACTORIES

GEOJSON_DIR = Path(__file__).parent / "fixtures" / "geojson"
GEOJSON_FIXTURES = sorted(GEOJSON_DIR.glob("*.geojson"))

# Non GeoJSON types and their expected GeoJSON type after export
SFCGAL_TO_GEOJSON_TYPE = {
    "Triangle": "Polygon",
    "TIN": "MultiPolygon",
    "PolyhedralSurface": "MultiPolygon",
    "Solid": "MultiPolygon",
    "MultiSolid": "GeometryCollection",
}


@pytest.mark.parametrize(
    "geom_factory",
    GEOMETRY_FACTORIES.values(),
    ids=GEOMETRY_FACTORIES.keys()
)
def test_geom_to_geojson(geom_factory):
    geom = geom_factory(0)
    geom_geojson = geom.to_geojson()
    other_geom = Geometry.from_geojson(geom_geojson)
    assert other_geom == geom


@pytest.mark.parametrize(
    "geom_factory",
    GEOMETRY_FACTORIES.values(),
    ids=GEOMETRY_FACTORIES.keys()
)
def test_geom_to_geojson_to_dict(geom_factory):
    """Test the correspondance between to_dict and to_geojson.

    These methods gives slightly differents outputs for Triangle and TIN, as the square
    bracket structures are not handled identically in SFCGAL and the Python binding.

    """
    geom = geom_factory(0)
    geom_dict = geom.to_dict()
    if geom.geom_type in ("Triangle", "TriangulatedSurface"):
        geom_dict["coordinates"] = [geom_dict["coordinates"]]
    geojson_str = json.dumps(geom_dict)
    json_geom = Geometry.from_geojson(geojson_str)
    assert json_geom == geom


@pytest.mark.parametrize(
    "geojson_file",
    GEOJSON_FIXTURES,
    ids=[f.stem for f in GEOJSON_FIXTURES],
)
def test_geojson_roundtrip(geojson_file: Path):
    """GeoJSON round-trip: read -> export -> re-read -> compare WKT."""
    geom = Geometry.read_geojson(geojson_file)
    roundtrip = Geometry.from_geojson(geom.to_geojson())
    assert geom.to_wkt() == roundtrip.to_wkt()


@pytest.mark.parametrize(
    "name, factory",
    [(n, f) for n, f in GEOMETRY_FACTORIES.items() if n in SFCGAL_TO_GEOJSON_TYPE],
    ids=[n for n in GEOMETRY_FACTORIES if n in SFCGAL_TO_GEOJSON_TYPE],
)
def test_sfcgal_type_to_geojson(name, factory):
    """Non GeoJSON types export to standard GeoJSON type when strict=True."""
    geom = factory(1.0)
    result = Geometry.from_geojson(geom.to_geojson(strict=True))
    assert result.geom_type == SFCGAL_TO_GEOJSON_TYPE[name]


def test_geojson_read_write_file(tmp_test_dir: Path):
    """Write/read GeoJSON file round-trip."""
    geom = Point(1.0, 2.0, 3.0)
    filepath = str(tmp_test_dir / "test.geojson")
    geom.write_geojson(filepath)
    assert Geometry.read_geojson(filepath) == geom


@pytest.mark.parametrize("value", [None, ""])
def test_from_geojson_returns_none_on_empty(value):
    """from_geojson returns None for None or empty string."""
    assert Geometry.from_geojson(value) is None


def test_to_geojson_precision():
    """to_geojson precision parameter controls decimal places."""
    geom = Point(1.123456789, 2.987654321)
    data_p3 = json.loads(geom.to_geojson(precision=3))
    data_p8 = json.loads(geom.to_geojson(precision=8))
    assert data_p3["coordinates"] == [1.123, 2.988]
    assert data_p8["coordinates"] == [1.12345679, 2.98765432]


def test_to_geojson_strict_converts_sfcgal_types():
    """to_geojson(strict=True) converts non-standard types to OGC equivalents."""
    tin = GEOMETRY_FACTORIES["TIN"](1.0)
    result_strict = json.loads(tin.to_geojson(strict=True))
    result_non_strict = json.loads(tin.to_geojson(strict=False))
    assert result_strict["type"] == "MultiPolygon"
    assert result_non_strict["type"] == "TIN"


def test_to_geojson_include_bbox():
    """to_geojson(include_bbox=True) adds a bbox field."""
    geom = Polygon([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    data_with = json.loads(geom.to_geojson(include_bbox=True))
    data_without = json.loads(geom.to_geojson(include_bbox=False))
    assert "bbox" in data_with
    assert "bbox" not in data_without
