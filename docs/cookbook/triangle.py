from pysfcgal import Triangle

# The constructor actually expects a sequence of three point coordinates.
triangle = Triangle([(1, 3), (3, 3), (3, 1)])
print(triangle)

# TRIANGLE ((1.00000000 3.00000000, 3.00000000 3.00000000,
# 3.00000000 1.00000000, 1.00000000 3.00000000))

# By the way, providing a closed sequence won't work as expected...
triangle = Triangle([(1, 3), (3, 3), (3, 1), (1, 3)])
print(triangle)

# TRIANGLE EMPTY
