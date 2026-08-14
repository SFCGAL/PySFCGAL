from pysfcgal import Tin, Triangle

# The constructor expects a sequence of triangle coordinates.
tin = Tin([((1, 3, 0), (3, 3, 0), (3, 1, 1))])
print(tin)

# TIN Z (((1.00000000 3.00000000 0.00000000, 3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000, 1.00000000 3.00000000 0.00000000)))

# As other collections, you may prefer instanciating an empty geometry
# and add patch sequentially
tin = Tin()
triangle = Triangle([(1, 3, 0), (3, 3, 0), (3, 1, 1)])
tin.add_patch(triangle)
print(tin)

# TIN Z (((1.00000000 3.00000000 0.00000000, 3.00000000 3.00000000 0.00000000,
# 3.00000000 1.00000000 1.00000000, 1.00000000 3.00000000 0.00000000)))
