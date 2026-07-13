---
title: Getting started
icon: fontawesome/solid/person-running
date: 2026-08-04
description: "Create your first PySFCGAL geometries"
tags:
    - documentation
    - user
---

# Getting started

This guide introduces the core concepts of PySFCGAL and shows how to create and manipulate geometries in just a few minutes.

By the end of this page, you will know:

- how geometries are represented in PySFCGAL;
- how to create the most common geometry types;
- how to inspect geometry properties;
- how to read and write geometries using standard formats.

For more detailed explanations and advanced use cases, see the [cookbook section](./cookbook.md).

---

## Geometry model

PySFCGAL extends the traditional geometry model defined by the [OGC Simple Features specification](https://www.ogc.org/standards/sfa/), a widely adopted standard used by many GIS applications and libraries, with advanced 3D geometry types and operations provided by [SFCGAL](https://sfcgal.gitlab.io/SFCGAL).

If you have already worked with libraries such as **PostGIS**, **Shapely** or **GeoPandas**, the geometry types and operations will already feel familiar.

The most common geometry types are:

| Geometry | Description |
|-----------|-------------|
| `Point` | A single position defined by coordinates |
| `LineString` | A sequence of connected points |
| `Polygon` | A planar surface bounded by one exterior ring and optional interior rings |
| `MultiPoint` | A collection of points |
| `MultiLineString` | A collection of line strings |
| `MultiPolygon` | A collection of polygons |
| `GeometryCollection` | A heterogeneous collection of geometries |

PySFCGAL also supports advanced geometry types such as `Triangle`, `TriangulatedSurface`, `PolyhedralSurface` and `Solid`, making it suitable for both 2D and 3D geometric processing.

| Geometry | Description |
|-----------|-------------|
| `Triangle` | A planar surface composed of three vertices |
| `TriangulatedSurface` | A set of connected triangles |
| `PolyhedralSurface` | A set of connected polygons |
| `Solid` | A 3D volume |
| `MultiSolid` | A collection of solids |

---

## Creating geometries

Most geometries can be created directly from Python coordinates.

### Point

```python
from pysfcgal import Point
point = Point(2.5, 48.8)
print(point)
```

```console
POINT (2.50000000 48.80000000)
```

### LineString

```python
from pysfcgal import LineString
line = LineString([
    (0, 0),
    (1, 2),
    (3, 1),
])
print(line)
```

```console
LINESTRING (0.00000000 0.00000000,1.00000000 2.00000000,3.00000000 1.00000000)
```

### Polygon

```python
from pysfcgal import Polygon

polygon = Polygon([
    (0, 0),
    (4, 0),
    (4, 3),
    (0, 3),
    (0, 0),
])

print(polygon)
```

```console
POLYGON ((0.00000000 0.00000000,4.00000000 0.00000000,4.00000000 3.00000000,0.00000000 3.00000000,0.00000000 0.00000000))
```

### MultiPoint

PySFCGAL supports the collection types, *e.g.* `MultiPoint`:


```python
from pysfcgal import MultiPoint

multipoint = MultiPoint(((0, 0), (1, 1), (2, 2)))

print(multipoint)
```

```console
MULTIPOINT ((0.00000000 0.00000000),(1.00000000 1.00000000),(2.00000000 2.00000000))
```

Like other collection types, a MultiPoint can also be built incrementally by adding individual points:

```python

multipoint = MultiPoint()
multipoint.add_point(Point(0, 0))
multipoint.add_point(Point(1, 1))
multipoint.add_point(Point(2, 2))
```

Most geometry classes follow the same construction pattern, making it easy to move from one geometry type to another. For other geometry types, see the [geometry creation section in the cookbook](./cookbook.md/#geometry-creation).

---

## Inspecting geometries

Geometry objects expose useful properties that can be queried directly from Python.

```python
print(point.x)
print(point.y)
```

```console
2.5
48.8
```

Many geometry types also expose geometric properties such as area, volume, dimension or validity.

```python
print(polygon.area)
```

```console
12.0
```

The available properties depend on the geometry type.

For a complete overview, see the [API reference](./api.md).

---

## Reading and writing geometries

PySFCGAL supports common geometry exchange formats:

- WKT
- WKB
- GeoJSON
- OBJ
- VTK (write-mode only)
- STL (write-mode only)

When relevant, PySFCGAL is able to directly read/write files.

Let's consider a first example that uses the WKT format.

### Read a WKT

The Well-Known Text (WKT) format is a textual representation of the geometries. PySFCGAL geometries may be instantiated from a WKT:

```python
from pysfcgal import Geometry

geometry = Geometry.from_wkt(
    "POLYGON((0 0,4 0,4 3,0 3,0 0))"
)
print(geometry)
```

```console
POLYGON ((0.00000000 0.00000000,4.00000000 0.00000000,4.00000000 3.00000000,0.00000000 3.00000000,0.00000000 0.00000000))
```

### Write a WKT

In PySFCGAL, the default WKT writer returns the fractional format, which denotes exact numerical precision.

```python
print(geometry.to_wkt())
```

```console
POLYGON ((0/1 0/1,4/1 0/1,4/1 3/1,0/1 3/1,0/1 0/1))
```

The function may be parametrized to get more human-readable outputs:

```python
print(geometry.to_wkt(1))
```

```console
POLYGON ((0.0 0.0, 4.0 0.0, 4.0 3.0, 0.0 3.0, 0.0 0.0))
```

---

## Working in 3D

Unlike many geometry libraries, PySFCGAL provides extensive support for 3D geometries.

Creating a 3D point is as simple as providing a third coordinate.

```python
point_3d = Point(0, 0, 12)

print(point_3d)
```

```console
POINT Z (0.00000000 0.00000000 12.00000000)
```

Many algorithms also support surfaces, solids and other volumetric geometries.

### Polyhedral surfaces

PySFCGAL supports advanced 3D geometries that are not available in many GIS libraries, namely the polyhedral surfaces.

Polyhedral surfaces can be used to model buildings, terrain elements or other 3D objects.

```python
from pysfcgal import PolyhedralSurface

phs = PolyhedralSurface()

face1 = Polygon(((0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)))
phs.add_patch(face1)
face2 = Polygon(((1, 1, 1), (1, 0, 1), (2, 0, 0), (2, 1, 0)))
phs.add_patch(face2)
```

Some advanced 3D processing are provided as examples in the [cookbook](./cookbook.md/#algorithms).

---

## Where to go next

You now know the basic concepts needed to start using PySFCGAL.

Continue with:

- The [cookbook](./cookbook.md) for more detailed explanations and advanced use cases.
- The [API reference](./api.md) for the complete list of classes and methods.

---

## Further reading

- [SFCGAL documentation](https://sfcgal.gitlab.io/SFCGAL/)
- [OGC simple feature standard](https://www.ogc.org/standards/sfa/)
