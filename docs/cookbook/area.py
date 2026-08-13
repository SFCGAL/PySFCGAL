from pysfcgal.geometry import Polygon, PolyhedralSurface

polygon_without_holes_wkt = "POLYGON ((0 0,10 0,10 10,0 10,0 0))"
polygon_without_holes = Polygon.from_wkt(polygon_without_holes_wkt)
print(f"polygon without holes - area: {polygon_without_holes.area}")
# polygon without holes - area: 100.0

polygon_holes_wkt = "POLYGON ((0 0,10 0,10 10,0 10,0 0),(3 3,3 7,7 7,7 3,3 3))"
polygon_holes = Polygon.from_wkt(polygon_holes_wkt)
print(f"polygon holes - area: {polygon_holes.area}")
# polygon holes - area: 84.0

cube_wkt = """POLYHEDRALSURFACE Z (
  ((0 0 0,1 0 0,1 1 0,0 1 0,0 0 0)),
  ((0 0 1,0 1 1,1 1 1,1 0 1,0 0 1)),
  ((0 0 0,0 1 0,0 1 1,0 0 1,0 0 0)),
  ((1 0 0,1 0 1,1 1 1,1 1 0,1 0 0)),
  ((0 0 0,0 0 1,1 0 1,1 0 0,0 0 0)),
  ((0 1 0,1 1 0,1 1 1,0 1 1,0 1 0))
)"""

cube = PolyhedralSurface.from_wkt(cube_wkt)
print(f"3D area: {cube.area_3d}")
# 3D area: 6.0
