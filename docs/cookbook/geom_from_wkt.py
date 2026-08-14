from pysfcgal import Geometry

# Build geometries from Well-Known Text representation

wkt_point = "POINT (1 3)"
geom = Geometry.from_wkt(wkt_point)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.surface.Polygon, 'Polygon'

wkt_linestring = "LINESTRING (1 3,3 3)"
geom = Geometry.from_wkt(wkt_linestring)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.curve.LineString, 'LineString'

wkt_polygon = "POLYGON ((1 3,3 3,3 1,1 1,1 3))"
geom = Geometry.from_wkt(wkt_polygon)
print(type(geom), geom.geom_type)

# pysfcgal.geometry.surface.Polygon, 'Polygon'
