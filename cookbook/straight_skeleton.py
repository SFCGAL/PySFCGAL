from pysfcgal.geometry import Geometry

wkt_polygon = "POLYGON ((0 0,10 0,10 5,5 5,5 2,0 2,0 0))"

input_polygon = Geometry.from_wkt(wkt_polygon)

skeleton = input_polygon.straight_skeleton()
print(skeleton.to_wkt(1))

# MULTILINESTRING ((0.0 0.0,1.0 1.0),
# (10.0 0.0,7.5 2.5),
# (10.0 5.0,7.5 2.5),
# (5.0 5.0,7.5 2.5),
# (5.0 2.0,6.0 1.0),
# (0.0 2.0,1.0 1.0),
# (1.0 1.0,6.0 1.0),
# (6.0 1.0,7.5 2.5))
