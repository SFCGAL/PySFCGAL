from pysfcgal import Point, Polygon

# Build geometries from GeoJSON-like representations (dict or str)

point_dict = {"type": "Point", "coordinates": [0.0, 0.0, 12.0]}
point = Point.from_dict(point_dict)
print(point)

# POINT Z (0.00000000 0.00000000 12.00000000)

point_geojson = '{"coordinates":[1.0,3.0],"type":"Point"}'
point = Point.from_geojson(point_geojson)
print(point)

# POINT (1.00000000 3.00000000)

polygon_dict = {
    "type": "Polygon",
    "coordinates": [[(1, 3), (3, 3), (3, 1), (1, 1), (1, 3)]],
}
polygon = Polygon.from_dict(polygon_dict)
print(polygon)

# POLYGON ((1.00000000 3.00000000,3.00000000 3.00000000,
# 3.00000000 1.00000000,1.00000000 1.00000000,1.00000000 3.00000000))

polygon_geojson = (
    '{"coordinates":[[[1.0,3.0],[3.0,3.0],[3.0,1.0],[1.0,1.0],[1.0,3.0]]],'
    '"type":"Polygon"}'
)
polygon = Polygon.from_geojson(polygon_geojson)
print(polygon)

# POLYGON ((1.00000000 3.00000000,3.00000000 3.00000000,
# 3.00000000 1.00000000,1.00000000 1.00000000,1.00000000 3.00000000))
