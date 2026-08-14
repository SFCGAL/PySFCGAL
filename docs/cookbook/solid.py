from pysfcgal import Polygon, PolyhedralSurface, Solid

# Let's add an additional dimension with respect to PolyhedralSurface: a Solid is a
# sequence of PolyhedralSurface.
solid = Solid([[[[(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 1)]]]])
print(solid)

# SOLID Z ((((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,1.00000000
# 3.00000000 1.00000000,1.00000000 3.00000000 0.00000000))))

# When initializing the solid as an empty geometry, one has to build a polyhedron first
solid = Solid()
phs = PolyhedralSurface()
polygon = Polygon([(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 0)])
phs.add_patch(polygon)
# first method: promote the PolyhedralSurface as a Solid
solid = phs.to_solid()
print(solid)

# SOLID Z ((((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,1.00000000
# 3.00000000 1.00000000,1.00000000 3.00000000 0.00000000))))

# second method: set the Solid exterior shell
solid.set_exterior_shell(phs)
print(solid)

# SOLID Z ((((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,1.00000000
# 3.00000000 1.00000000,1.00000000 3.00000000 0.00000000))))
