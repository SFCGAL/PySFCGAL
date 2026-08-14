from pysfcgal import Geometry

# Build geometries from Well-Known Binary representation;
# the geometries in PostGIS dumps are typically represented in this format

wkb_point = "01e9030000000000000000000000000000000000000000000000002840"
geom = Geometry.from_wkb(wkb_point)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.point.Point, 'Point'

wkb_linestring = "010200000002000000000000000000f03f000000000000084000000000000008400000000000000840"  # noqa: E501
geom = Geometry.from_wkb(wkb_linestring)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.curve.LineString, 'LineString'

wkb_polygon = "01eb0300000100000005000000000000000000f03f000000000000084000000000000000000000000000000840000000000000084000000000000000000000000000000840000000000000f03f000000000000f03f000000000000f03f000000000000f03f000000000000f03f000000000000f03f00000000000008400000000000000000"  # noqa: E501
geom = Geometry.from_wkb(wkb_polygon)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.surface.Polygon, 'Polygon'
