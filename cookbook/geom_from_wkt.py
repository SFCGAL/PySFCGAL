from pysfcgal.geometry import Geometry

wkt_point = "POINT (1 3)"
wkt_linestring = "LINESTRING (1 3,3 3)"
wkt_polygon = "POLYGON ((1 3,3 3,3 1,1 1,1 3))"

point = Geometry.from_wkt(wkt_point)
linestring = Geometry.from_wkt(wkt_linestring)
polygon = Geometry.from_wkt(wkt_polygon)

print(type(polygon))
# pysfcgal.sfcgal.Polygon
