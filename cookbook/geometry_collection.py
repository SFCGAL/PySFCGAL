from pysfcgal.geometry import GeometryCollection, LineString, Point, Polygon

point = Point(1, 3)
linestring = LineString([(1, 3), (3, 1)])
polygon = Polygon([(1, 3), (3, 3), (3, 1), (1, 1), (1, 3)])

collection = GeometryCollection()

collection.add_geometry(point)
collection.add_geometry(linestring)
collection.add_geometry(polygon)
