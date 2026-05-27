from pysfcgal import sfcgal

point = sfcgal.Point(1, 3)
linestring = sfcgal.LineString([(1, 3), (3, 1)])
polygon = sfcgal.Polygon([(1, 3), (3, 3), (3, 1), (1, 1), (1, 3)])

collection = sfcgal.GeometryCollection()

collection.add_geometry(point)
collection.add_geometry(linestring)
collection.add_geometry(polygon)
