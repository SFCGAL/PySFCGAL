# PySFCGAL Changelog

## v2.3.0 (2026-06-19)

This version follows the changes upstream on the SFCGAL side (see [the SFCGAL documentation](https://sfcgal.gitlab.io/SFCGAL/history/#changelog-sfcgal-230-2026-06-12)).

Disclaimer: the NURBSCurve are not implemented yet in PySFCGAL.

### Feat

- **geometry**: add chamfer/fillet
- **polygon**: add sk extrude variants with per-edge weights
- **polygon**: add extrude_polygon_straight_skeleton_with_angles
- **geometry**: Add support for mirror operation
- **vector**: Add normalize operator
- **geometry**: Add support for split_3d algorithm
- Add insert_points_within_tolerance algorithm
- **pysfcgal/geometry/geometry.py**: improve *geojson methods
- **pysfcgal/geometry/geometry.py**: implement from_geojson and to_geojson
- **primitive**: Add support for scale
- **primitive**: Add support for rotation
- **primitive**: Add support for center
- **primitive**: Add support for translate operation
- **pysfcgal**: Introduce a Vector3D class
- **primitive**: Add a property to retrieve primitive transformation
- **pysfcgal/geometry/surface.py**: set n-th patch for Tin and PolyhedralSurface
- **primitive**: Add logic to clone a primitive
- **primitive**: Add support for equality operator
- **cookbook**: Add GDAL export example
- **collection**: Add support to set the nth geometry of a collection
- surface edge number
- implement the surface simplification algorithm from the C API
- **linestring**: Add add_point method
- Add a deprecation mechanism
- **sfcgal**: Add a unified API for rotation
- **sfcgal**: Add support for boundary
- define a property setter
- checking the geometry validity updates its validity flag
- exploit the SFCGAL validity flag
- Add primitive support
- add OBJ reader methods
- **sfcgal**: Implement linestring close method
- Add roof related API
- **sfcgal**: Add support for extrude_straight_skeleton_with_angles
- **check_api_coverage**: Add support to hanlde multiple python files
- **sfcgal**: Add extend to edges option to approximate_medial_axis
- implement centroid functions
- Add polyhedral surface to multi polygon converter
- use the sfcgal_geometry_geom_type function from the C API
- Allow to retrieve buffer types values as string
- **sfcgal**: Update c file to ignore CGAL 6 functions
- **scripts/update_def**: Ignore CGAL 6 functions
- **sfcgal**: Add support for polygon set_exterior_ring
- **sfcgal**: Add the geometry's dimension as a property
- **sfcgal**: Add support for geometry is_simple_detail
- **sfcgal**: Add support for geometry is_simple
- **sfcgal**: Add support for is_closed
- fixes
- Add a script to check api coverage
- **sfcgal**: Update c file from latest SFCGAL devs
- **sfcgal**: Add support for linestring add_interior_ring
- **sfcgal**: Add support for swap_xy
- **sfcgal**: Add support for force_z and force_m
- **sfcgal**: Add support for drop_z and drop_m
- **sfcgal**: Improve is_valid_detail docstring

### Fix

- **polygon**: raise ValueError on empty ring in _validate_ring_values
- **geometry**: Fix indentation in split_3d docstring
- **collection**: Fix parent in Geometry.from_sfcgal_geometry calls
- **cookbook/export_geometry.py**: rename to export_gpkg.py
- **cookbook**: Fix linestring wkt example in geom_from_wkt
- **scripts/check_api_coverage.py**: consider every Python modules
- **setup.py**: use setuptools find_package to get every subpackages
- **sfcgal**: Protect against null wkt in Geometry.from_wkt
- **check_api_coverage**: Add support for reference in c parsing
- **sfcgal**: Properly handle memory management on subgeometries
- **tests**: Use a valid tin fixture
- **tests**: Use a valid polyhedralsurface fixture
- **sfcgal**: Change default wrapped value for tin to multi_polygon
- **ci**: Ensure to start docker for windows wheel job
- **tests**: Fix alphashapes unit test for SFCGAL 2.3
- **scripts/update_def**: Fix windows_version typing
- **update_def**: Fix doxygen parser if block is not a function
- **docs/cookbook**: Fix paragraphs indentation
- **sfcgal**: Fix memory leak in is_valid_detail

### Refactor

- **polygon**: move sk extrude methods from Geometry to Polygon
- **primitive**: Adapt to upstream primitives changes
- **check_api_coverage**: Ignore sfcgal_prepared_geometry_as_geojson
- **primitive**: Add missing annotations to the stub file
- **capi**: Update c api files
- **geometry**: Do not use deprecated 2d suffix in rotate
- **geometry.py**: area_3d and volume are properties
- **cookbook**: Switch to the new import logic
- **roof**: Directly use c lib in PrimitiveType
- **simplification**: Directly use c lib in SimplificationStrategy
- **roof**: Directly use c lib in RoofType
- **buffer**: Directly use c lib in BufferType
- **roof**: Fix deprecated import warning
- **primitive**: Fix deprecated import warning
- **capi**: Update c api files
- **collection**: Mark addGeometry as deprecated
- **cookbook**: Do not use deprecated addGeometry
- **geometry**: Mark translate_2d as deprecated
- move Solid to volume.py
- **pysfcgal/sfcgal.py**: split the main module into smaller modules
- **sfcgal**: Simplify Geometry.to_wkt
- **sfcgal**: Deprecate tessellate method
- API break change tessellate behavior
- **sfcgal**: Improve triangulate_2dz documentation
- **scripts/api_coverage**: Ignore rotate default values
- **sfcgal**: Deprecate previous rotation API
- **sfcgal**: Fix simplify parameters naming convention
- **tests**: Move some polygon fixtures to the base conftest
- **pysfcgal**: Move contract logic to its own module
- **sfcgal**: Move lib init to __init__
- **capi**: Update c api files
- **tests/utils.py**: design simple geometry factories
- **tests/test_wkt.py**: add tests for to_wkt/from_wkt
- **pysfcgal**: Update solid and multisolid type ids
- **docs/cookbook**: Improve structure

## v2.2.0 (2025-07-31)

### Feat

- **IO**: Add STL export

### Fix

- **sfcgal**: Adapt to Extrude Straigth Skeleton roof fixed

### Build

- **ci**: Build a macos wheel

## v2.1.0 (2025-05-14)

### BREAKING CHANGE

- `straight_skeleton` method now returns a polyhedral surface instead of a multi-polygon

### Feat

- **docs**: Add straight_skeleton cookbook example
- **docs**: Add a cookbook section to provide some examples
- **sfcgal**: Add support for alpha_wrapping_3d
- **sfcgal**: Add a method to add an interior shell to a solid
- **sfcgal**: Add a method to set the exterior shell of a solid
- **sfcgal**: Allow to add a solid to a multisolid
- **sfcgal**: Allow to add a patch to a polyhedralsurface
- **sfcgal**: Allow to add a patch to a tin
- **sfcgal**: Allow to add a polygon to a multipolygon
- **sfcgal**: Allow to add a linestring to a multilinestring
- **sfcgal**: Allow to add a point to a multipoint
- **sfcgal**: Add add_geometry to GeometryCollection
- **sfcgal**: Allow to add geometry in a GeometryCollectionBase
- add simplify function from SFCGAL
- 3D tessellation support
- **update_def**: Add support for the new SFCGAL deprecated mechanism
- **sfcgal.py**: Added an alias method for translate. | To ensure consistency in function naming, do not use 2d in function names.

### Fix

- **sfcgal**: A Solid is not a geometry collection
- **sfcgal**: Rename TIN docstring according to patch terminology
- **sfcgal**: A TIN is not a geometry collection
- **sfcgal**: Rename PolyhedralSurface docstring according to patch
- **sfcgal**: A PolyhedralSurface is not a geometry collection
- **sfcgal**: builds an empty Polygon
- **sfcgal**: builds an empty LineString
- **sfcgal**: handle wrong Point constructor parametrization
- **sfcgal**: builds empty Tin and PolyhedralSurface
- **test_straight_skeleton**: skeleton is now a polyhedralSurface
- **build**: Add missing long_description_content_type to setup.py
- **update_def**: Remove spurious print
- **docs/docs/build.md**: do not recommend to directly invoke setup.py
- prevent a segfault in CoordinateSequence
- wrong documentation dependency version
- **sfcgal**: Fix multisolid default constructor
- **sfcgal**: Fix solid default constructor
- **sfcgal**: Fix multipolygon default constructor
- **sfcgal**: Fix multilinestring default constructor
- **sfcgal**: Fix multipoint default constructor
- **sfcgal**: Fix is_valid_detail
- buffer_3d should not accept segments=3

## v2.0.0 (2024-09-26)

### BREAKING CHANGE

The following functions have been removed, and replaced by methods in the geometry classes:

- pysfcgal.sfcgal.shape
- pysfcgal.sfcgal._shape
- pysfcgal.sfcgal.point_from_coordinates
- pysfcgal.sfcgal.linestring_from_coordinates
- pysfcgal.sfcgal.triangle_from_coordinates
- pysfcgal.sfcgal.polygon_from_coordinates
- pysfcgal.sfcgal.multipoint_from_coordinates
- pysfcgal.sfcgal.multilinestring_from_coordinates
- pysfcgal.sfcgal.multipolygon_from_coordinates
- pysfcgal.sfcgal.tin_from_coordinates
- pysfcgal.sfcgal.geometry_collection_from_coordinates
- pysfcgal.sfcgal.polyhedralsurface_from_coordinates
- pysfcgal.sfcgal.solid_from_coordinates
- pysfcgal.sfcgal.mapping
- pysfcgal.sfcgal.point_to_coordinates
- pysfcgal.sfcgal.linestring_to_coordinates
- pysfcgal.sfcgal.polygon_to_coordinates
- pysfcgal.sfcgal.multipoint_to_coordinates
- pysfcgal.sfcgal.multilinestring_to_coordinates
- pysfcgal.sfcgal.multipolygon_to_coordinates
- pysfcgal.sfcgal.geometrycollection_to_coordinates
- pysfcgal.sfcgal.triangle_to_coordinates
- pysfcgal.sfcgal.tin_to_coordinates
- pysfcgal.sfcgal.polyhedralsurface_to_coordinates
- pysfcgal.sfcgal.solid_to_coordinates
- pysfcgal.sfcgal.triangle_to_polygon
- pysfcgal.sfcgal.tin_to_multipolygon
- pysfcgal.sfcgal.solid_to_polyhedralsurface

### Feat

- Polyhedralsurface.to_solid()
- update sfcgal_def_msvc
- update C API after recent changes in SFCGAL
- 2D- and 3D-translations
- convert the IO functions as new Geometry class methods
- scale operations
- write geometries as VTK/OBJ files/strings
- implement rotation operations
- buffer 3D on Point and LineString
- straight skeleton partition
- support MultiSolid

### Fix

- add C files to package_data
- fix the Python image name in the CI jobs
- do not directly invoke setup.py to build windows package
- Geometry.extrude() returns a Solid instead of a PolyhedralSurface
- fix vtk functions
- fix memory issue by using lib.sfcgal_geometry_clone
- **test**: Fix WKT in tests after https://gitlab.com/sfcgal/SFCGAL/-/merge_requests/361
- icontract decorators must have a lambda as the first parameter
- call the same decorator several times

### Refactor

- split test on geometries, a module per geometry type
- build geometries from coordinates and geojson-like data
- geom-to-coordinates converters as geometry class methods
- wrap_geom becomes a method of the Geometry class
- geom1_to_geom2 converters considered as geometry class methods

## Version 1.5.2 (2024-07-25)

### New Features
- Add Solid high-level interface (!40, Raphaël Delhome)
- Add GeometryCollection high-level interface (!39, Raphaël Delhome)
- Add Triangle and Tin high-level interface (!38, Raphaël Delhome)
- Add PolyhedralSurface high-level interface (!37, Raphaël Delhome)
- Add Multi-geometries high-level interface (!33, Raphaël Delhome)
- Add Polygon high-level interface (!32, Raphaël Delhome)
- Add LineString high-level interface (!29, Raphaël Delhome)
- Add extrude (!17, Florent Fougères)
- Add VTK export (!18, Loïc Bartoletti)

### Improvements
- Fix a typo in tin_from_coordinates and add a test (!35, Loïc Bartoletti)
- Update wkb to handle binary and hex wkb (!23, Loïc Bartoletti)
- Improve installation documentation (!20, Florent Fougères)

### CI/CD
- Build windows wheel (!21, Jean Felder)
- Add a flake8 job (!26, Jean Felder)

### Tests
- Add force_lhr and force_rhr test (!34, Loïc Bartoletti)
- Fix visibility algorithm test (!24, Loïc Bartoletti)

### Other
- Switch to GPLv3+ (!22, Raphaël Delhome)

## Version 1.5.1 (2023-12-21)

### Improvements
- Update build instructions for Unix and add for Windows
- Add detection for MSVC bugs on CGAL
- Update sfcgal_def.c file to remove #if/#endif for MSVC

### Fixes
- Fix exception message for Python versions
- Update update_def.sh script to handle #if/#endif for MSVC/CGAL bugs on alpha shapes

### Other
- Replace gitlab.com/Oslandia with gitlab.com/SFCGAL

## Version 1.5.0 (2023-10-31)

### New Features
- Add support for visibility
- Add has_exterior_vertex method for polygons
- Add Python bindings support for straight skeleton extrusion
- Add WKB read/write
- Add partition function
- Add high-level interface for Polygon

### Improvements
- Modernize property declarations
- Update SFCGAL C API

### Fixes
- Fix parameters in partition contracts
- Fix crash in wrap_geom

### Tests
- Add tests for straight skeleton extrusion and visibility

## Version 1.4.1 (2022-01-27)

### New Features
- Add linesubstring and alpha_shapes
- Add sfcgal_full_version
- Add convexhull and convexhull_3D
- Add polyhedral_surface
- Add intersects_3d and intersection_3d
- Add union and union_3d

### Improvements
- Use typing and minor fixes
- Import icontract for DbC (Design by Contract)
- Add missing methods (line_sub_string, orientation, is_planar, covers_3d, volume for solids)
- Improve point constructor with m value

### Dependencies
- Add icontract as a dependency

### Tests
- Add numerous tests for new features

### Other
- Align version with SFCGAL

## Version 0.1.0 (2020-07-27)

### New Features
- Add minkowski_sum, straight_skeleton, and others
- Add TIN and triangulation support
- Add difference and force_{l,r}hr
- Add Point.z and Point.has_z properties
- Add access to linestring coordinates
- Add access to geometry collection geometries via .geoms

### CI/CD
- Add Cirrus CI

### Fixes
- Fix memory leaks
- Fix path for ffibuilder

### Other
- Initial project commit
