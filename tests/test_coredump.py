import signal
from subprocess import PIPE, CalledProcessError, run

import pytest

from pysfcgal import LineString, Triangle


def test_wrap_geom_segfault():
    segfault_code = """
from pysfcgal.geometry import Triangle
triangle = Triangle([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
for t in [triangle, triangle]:
    triangle = Triangle.from_sfcgal_geometry(triangle._geom)
    """
    proc = run(("python3", "-c", segfault_code), stdout=PIPE, stderr=PIPE)
    assert proc.returncode in (-signal.SIGSEGV, -signal.SIGBUS)
    with pytest.raises(CalledProcessError):
        proc.check_returncode()


def test_wrap_geom():
    triangle = Triangle([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
    for t in [triangle, triangle]:
        triangle = triangle.wrap()
    assert True  # Just to confirm that the code works fine and no segfault arises


def test_linestring_coord_sequence():
    linestring = LineString([(0, 0), (1, 0), (1, 1)])
    for coords in linestring.coords:
        print(coords)
    print(linestring)
    assert True  # Just to confirm that the code works fine and no segfault arises
