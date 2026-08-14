from pysfcgal import MultiSolid, Polygon, PolyhedralSurface, Solid

# Let's add another additional dimension with respect to Solid: a MultiSolid is a
# collection of Solid. The MultiSolid is then instanciated with a 6-dimension coordinate
# structure... (That's the PySFCGAL record. :-) )
multisolid = MultiSolid([[[[[(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 1)]]]]])
print(multisolid)

# MULTISOLID Z (((((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,1.00000000
# 3.00000000 1.00000000,1.00000000 3.00000000 0.00000000)))))

# As for the other collections, one may add new items gradually
multisolid = MultiSolid()
solid = Solid()
phs = PolyhedralSurface()
polygon = Polygon([(1, 3, 0), (3, 3, 0), (3, 1, 1), (1, 1, 1), (1, 3, 0)])
phs.add_patch(polygon)
solid.set_exterior_shell(phs)
multisolid.add_solid(solid)
print(multisolid)

# MULTISOLID Z (((((1.00000000 3.00000000 0.00000000,3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000,1.00000000 1.00000000 1.00000000,1.00000000
# 3.00000000 1.00000000,1.00000000 3.00000000 0.00000000)))))
