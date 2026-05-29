from pysfcgal.primitive import Sphere

# Create a sphere with default parameters
# radius = 1.0
# center at (0, 0, 0)
sphere = Sphere()
print(sphere.radius)
# 1.0
print(sphere.num_subdivisions)
# 1

# Create a sphere with custom_parameters
sphere = Sphere(radius=2.5, num_subdivisions=2)
print(sphere.radius)
# 2.5
print(sphere.num_subdivisions)
# 2

# Modify parameters via properties or dictionary-style access
sphere.radius = 2.0
print(sphere.radius)
# 2.0

sphere["radius"] = 5.0
print(sphere["radius"])
# 5.0

# Compute area and volume
print(sphere.volume())
# 523.5987755982987
print(sphere.area())
# 314.15926535897927

# Generate a polyhedral surface representation
phs = sphere.to_polyhedral_surface()
print(phs.to_wkt(6))
# POLYHEDRALSURFACE Z (((...)))
