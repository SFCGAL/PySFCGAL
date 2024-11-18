from pysfcgal import sfcgal

multilinestring = sfcgal.MultiLineString([[(1, 1), (2, 2)], [(3, 3), (4, 4)]])
print(multilinestring)

# MULTILINESTRING ((1.00000000 1.00000000,2.00000000 2.00000000),
# (3.00000000 3.00000000,4.00000000 4.00000000))
