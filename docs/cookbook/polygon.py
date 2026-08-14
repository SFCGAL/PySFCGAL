from pysfcgal import Polygon

polygon = Polygon([(1, 3), (3, 3), (3, 1), (1, 1), (1, 3)])
print(polygon)

# POLYGON ((1.00000000 3.00000000, 3.00000000 3.00000000,
# 3.00000000 1.00000000, 1.00000000 1.00000000,
# 1.00000000 3.00000000))

# The constructor also supports unclosed coordinate sequences, the result is similar.
polygon = Polygon([(1, 3), (3, 3), (3, 1), (1, 1)])
print(polygon)

# POLYGON ((1.00000000 3.00000000, 3.00000000 3.00000000,
# 3.00000000 1.00000000, 1.00000000 1.00000000,
# 1.00000000 3.00000000))
