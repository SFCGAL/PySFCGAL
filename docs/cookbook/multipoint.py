from pysfcgal import MultiPoint, Point

multipoint = MultiPoint(((1, 3), (3, 1)))
print(multipoint)

# MULTIPOINT ((1.00000000 3.00000000),(3.00000000 1.00000000))

# As other collections, you may prefer instanciating an empty geometry
# and add items sequentially
multipoint = MultiPoint()
print(multipoint)

# MULTIPOINT EMPTY

point = Point(1, 3)
multipoint.add_point(point)
print(multipoint)

# MULTIPOINT ((1.00000000 3.00000000),(3.00000000 1.00000000))
