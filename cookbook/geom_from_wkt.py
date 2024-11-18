from pysfcgal import sfcgal

wkt_point = "POINT (1 3)"
wkt_linestring = "LINESTRING ((1 3),(3 3))"
wkt_polygon = "POLYGON ((1 3,3 3,3 1,1 1,1 3))"

point = sfcgal.Geometry.from_wkt(wkt_point)
linestring = sfcgal.Geometry.from_wkt(wkt_linestring)
polygon = sfcgal.Geometry.from_wkt(wkt_polygon)

print(type(polygon))
# pysfcgal.sfcgal.Polygon
