import numpy as np

from pysfcgal.geometry import LineString, Point, Polygon

# -----------------------------------------------------------------------------
# Point to NumPy array
# -----------------------------------------------------------------------------
pt = Point.from_wkt("POINT (2 4 5)")
pt_array = np.asarray(pt.coords)
print(pt_array)
# array([2. 4. 5.])

# -----------------------------------------------------------------------------
# LineString to NumPy array
# -----------------------------------------------------------------------------
line = LineString.from_wkt("LINESTRING (3 0 0, 5 2 0, 12 4 1)")
line_array = np.asarray(line.coords)
print(line_array)
# array([[ 3.  0.  0.]
#        [ 5.  2.  0.]
#        [12.  4.  1.]])

# -----------------------------------------------------------------------------
# Polygon to NumPy arrays
# -----------------------------------------------------------------------------
# Exterior and interior rings are handled separately.
polygon = Polygon.from_wkt(
    "POLYGON Z ((0 0 0,10 0 0,10 10 0,0 10 0,0 0 0),"
    "(2 2 0,2 4 0,4 4 0,4 2 0,2 2 0),"
    "(6 6 0,6 8 0,8 8 0,6 6 0))"
)
exterior_array = np.asarray(polygon.exterior.coords)
print(exterior_array)
print(exterior_array.shape)
# array([[ 0.  0.  0.]
#        [10.  0.  0.]
#        [10. 10.  0.]
#        [ 0. 10.  0.]
#        [ 0.  0.  0.]])
#
# (5, 3)

# Interior rings are returned as a list of NumPy arrays because
# each ring may contain a different number of vertices.
interior_rings = [np.asarray(ring.coords) for ring in polygon.interiors]
print(interior_rings)
# [
#  array([[2., 2., 0.],
#        [2., 4., 0.],
#        [4., 4., 0.],
#        [4., 2., 0.],
#        [2., 2., 0.]]),
#  array([[6., 6., 0.],
#        [6., 8., 0.],
#        [8., 8., 0.],
#        [6., 6., 0.]])
# ]
