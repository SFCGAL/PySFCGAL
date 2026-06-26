import os
import platform
import subprocess

from cffi import FFI


def _pkg_config_available():
    """Check once whether pkg-config finds SFCGAL."""
    try:
        subprocess.run(
            ["pkg-config", "--exists", "sfcgal"],
            capture_output=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _pkg_config(option):
    try:
        result = subprocess.run(
            ["pkg-config", option, "sfcgal"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


_USE_PKG_CONFIG = _pkg_config_available()


def _get_include_dirs():
    if _USE_PKG_CONFIG:
        return [flag[2:] for flag in _pkg_config("--cflags-only-I")]
    elif "INCLUDE_PATH" in os.environ:
        return os.environ["INCLUDE_PATH"].split(os.pathsep)
    return []


def _get_library_dirs():
    if _USE_PKG_CONFIG:
        return [f[2:] for f in _pkg_config("--libs-only-L")]
    elif "LIBPATH" in os.environ:
        return os.environ["LIBPATH"].split(os.pathsep)
    return []


def _get_libraries():
    if _USE_PKG_CONFIG:
        return [f[2:] for f in _pkg_config("--libs-only-l")]
    elif "SFCGAL_LIBNAME" in os.environ:
        return [os.environ["SFCGAL_LIBNAME"]]
    return ["SFCGAL"]


ffibuilder = FFI()

ffibuilder.set_source(
    "pysfcgal._sfcgal",
    r"""
#include <stdlib.h>
#include <SFCGAL/capi/sfcgal_c.h>
""",
    libraries=_get_libraries(),
    library_dirs=_get_library_dirs(),
    include_dirs=_get_include_dirs(),
)

# Required until Alpha Shapes bug is not fixed on MSVC
compiler = platform.python_compiler()

sfcgal_c_file = "sfcgal_def_msvc.c" if ('MSC' in compiler) else "sfcgal_def.c"

with open(os.path.join(os.path.dirname(__file__), sfcgal_c_file), "r") as f:
    sfcgal_def = f.read()

ffibuilder.cdef(sfcgal_def)

if __name__ == "__main__":
    help(ffibuilder.compile)
    ffibuilder.compile(verbose=True)
