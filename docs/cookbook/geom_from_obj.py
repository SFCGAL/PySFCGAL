from pysfcgal import Geometry

# When reading OBJ-like structures, SFCGAL builds multigeometries.

# point.obj
# v 1 3 0
# p 1

point_obj = "v 1 3 0\np 1\n"
geom = Geometry.from_obj(point_obj)
print(geom)

# MULTIPOINT Z ((1.00000000 3.00000000 0.00000000))

# linestring.obj
# v 1 3 0
# v 3 3 0
# l 1 2
linestring_obj = "v 1 3 0\nv 3 3 0\nl 1 2\n"
geom = Geometry.from_obj(linestring_obj)
print(geom)

# MULTILINESTRING Z ((1.00000000 3.00000000 0.00000000,
# 3.00000000 3.00000000 0.00000000))

# polygon.obj
# v 1 3 0
# v 3 3 0
# v 3 1 0
# v 1 1 0
# f 1 2 3 4
polygon_obj = "v 1 3 0\nv 3 3 0\nv 3 1 0\nv 1 1 0\nf 1 2 3 4\n"
geom = Geometry.from_obj(polygon_obj)
print(geom)

# POLYHEDRALSURFACE Z (((1.00000000 3.00000000 0.00000000,
# 3.00000000 3.00000000 0.00000000,3.00000000 1.00000000 0.00000000,
# 1.00000000 1.00000000 0.00000000,1.00000000 3.00000000 0.00000000)))

# When several object are stored into an OBJ file,
# SFCGAL considers faces as a priority, thus builds polyhedra.

# collection.obj
# v 0 0 2
# v 0 1 2
# v 1 3 0
# v 3 3 0
# v 3 1 0
# v 1 1 0
# p 1
# l 2 3
# f 4 5 3 6

collection_obj = (
    "v 0 0 12\n"
    "v 0 1 2\n"
    "v 3 1 0\n"
    "v 1 3 0\n"
    "v 3 3 0\n"
    "v 1 1 0\n"
    "p 1\n"
    "l 2 3\n"
    "f 4 5 3 6\n"
)
geom = Geometry.from_obj(collection_obj)
print(geom)

# POLYHEDRALSURFACE Z (((1.00000000 3.00000000 0.00000000,
# 3.00000000 3.00000000 0.00000000,3.00000000 1.00000000 0.00000000,
# 1.00000000 1.00000000 0.00000000,1.00000000 3.00000000 0.00000000)))
