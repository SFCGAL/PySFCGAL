from pysfcgal import Polygon, PolyhedralSurface

# Be careful to the dimension of the coordinates. One gets four dimensions, respectively
# for
# (i) a sequence of Polygon,
# (ii) and sequence of Polygon rings for each Polygon,
# (iii) and sequence of points into each ring
# and (iv) a tuple for point coordinates.
phs = PolyhedralSurface([[[(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 1)]]])
print(phs)

# POLYHEDRALSURFACE Z (((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000
# 0.00000000,3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,
# 1.00000000 3.00000000 0.00000000)))

# It sounds reasonable to use the empty geometry trick...
phs = PolyhedralSurface()
polygon = Polygon([(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 1)])
phs.add_patch(polygon)
print(phs)

# POLYHEDRALSURFACE Z (((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000
# 0.00000000,3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,
# 1.00000000 3.00000000 0.00000000)))
