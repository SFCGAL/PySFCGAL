from typing import Any

from osgeo import gdal, ogr, osr

from pysfcgal.geometry import Geometry


def add_geometry_to_layer(
        layer: ogr.Layer, geometry: Geometry, fields: dict[str, Any]) -> None:
    """
    Add a SFCGAL geometry to an OGR layer using WKB export.
    """
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetGeometry(ogr.CreateGeometryFromWkb(geometry.to_wkb()))
    for field_name, field_value in fields.items():
        feature.SetField(field_name, field_value)

    layer.CreateFeature(feature)


if __name__ == "__main__":
    gdal.UseExceptions()

    # Constants
    filename = "output.gpkg"
    layer_name = "extrusion"
    crs_id = 3857

    # Create a polygon and extrude it
    input_polygon = Geometry.from_wkt("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))")
    extruded_polygon = input_polygon.extrude_polygon_straight_skeleton(3.5, 0.6)

    # Create gpkg
    gpkg_driver = ogr.GetDriverByName("GPKG")
    if gpkg_driver is None:
        raise RuntimeError("GPKG driver is not available")

    with gpkg_driver.CreateDataSource(filename) as ds:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(crs_id)
        layer = ds.CreateLayer(layer_name, srs, geom_type=ogr.wkbPolyhedralSurfaceZ)
        fields_def: dict[str, int] = {"id": ogr.OFTInteger}
        for field_name, field_type in fields_def.items():
            field = ogr.FieldDefn(field_name, field_type)
            layer.CreateField(field)

        # Add SFCGAL geometry to the gpkg layer
        add_geometry_to_layer(layer, extruded_polygon, {"id": 1})
