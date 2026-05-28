#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from typing import List, Tuple

IGNORED_FUNCTIONS = {
    "free",
    "sfcgal_geometry_as_text",  # sfcgal_geometry_as_text_decim is used instead
    "sfcgal_geometry_rotate",  # sfcgal_geometry_rotate_2d is used instead
    "sfcgal_geometry_rotate_3d",  # sfcgal_geometry_rotate_3d_around_center is used instead  # noqa: E501
    "sfcgal_io_read_binary_prepared",
    "sfcgal_io_read_ewkt",
    "sfcgal_io_write_binary_prepared",
    "sfcgal_prepared_geometry_create",
    "sfcgal_prepared_geometry_create_from_geometry",
    "sfcgal_prepared_geometry_as_ewkt",
    "sfcgal_prepared_geometry_delete",
    "sfcgal_prepared_geometry_geometry",
    "sfcgal_prepared_geometry_set_geometry",
    "sfcgal_prepared_geometry_set_srid",
    "sfcgal_prepared_geometry_srid",
    "sfcgal_primitive_parameter",  # already covered by specialized primitive getters
    "sfcgal_primitive_set_parameter",  # already covered by specialized primitive setters  # noqa: E501
    "sfcgal_set_alloc_handlers",
    "sfcgal_set_error_handlers",
}


def extract_functions_from_c_file(c_file_path: Path) -> List[str]:
    """
    Extract all the function declaration from a .c/.h file

    Parameters
    ----------
    c_file_path : Path
        .c/.h file location

    Returns
    -------
    List[str]
        the name of the C functions as string
    """
    functions: List[str] = []

    try:
        with open(c_file_path, "r") as c_file:
            content = c_file.read()

        # Regex to detect function declaration
        # Pattern: Standard function declaration
        #   Matches: double sfcgal_point_x(const sfcgal_geometry_t *geom);
        #            void sfcgal_linestring_add_point(sfcgal_geometry_t *linestring, sfcgal_geometry_t *point);   # noqa: E501
        #   Captures: "sfcgal_point_x", "sfcgal_linestring_add_point"
        #
        # Breakdown of the regex:
        #   ^\s*                         - Start of the line, optional whitespace.
        #   [a-zA-Z_][a-zA-Z0-9_*\s]*    - The return type (e.g., int, void, ..).
        #   \s+                          - spaces before the function name.
        #   ([a-zA-Z_][a-zA-Z0-9_]*)     - CAPTURE GROUP: The function name itself.
        #   \s*\([^)]*\)\s*;             - The parameter list in parentheses
        pattern = r"^\s*[a-zA-Z_][a-zA-Z0-9_*\s]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*;"  # noqa: E501
        matches = re.findall(pattern, content, re.MULTILINE)
        functions.extend(matches)

        # Drop ignored functions
        functions = list(set(functions) - IGNORED_FUNCTIONS)

    except FileNotFoundError:
        print(f"Error: Unable to find C file {c_file_path}", file=sys.stderr)
        return []
    except Exception as exception:
        print(f"Error while reading C file: {exception}", file=sys.stderr)
        return []

    # Drop duplicates and sort
    return sorted(list(set(functions)))


def check_function_usage_in_python(
    py_file_paths: List[Path], function_names: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Check that all the C functions are used in the python file

    Parameters
    ----------
    py_file_path : Path
        python file location
    function_names : List[str]
        c functions to check

    Returns
    -------
    Tuple[List[str], List[str]]
        used C functions
        unused C functions
    """
    used_functions = set()

    for py_file_path in py_file_paths:
        try:
            with open(py_file_path, "r") as py_file:
                py_content = py_file.read()

            for func_name in function_names:
                # Look for the c function in the python code
                # Possible patterns: func_name(, .func_name(, lib.func_name(
                patterns = [
                    rf"\b{re.escape(func_name)}\b",  # direct call, reference, or via object  # noqa: E501
                    rf'"{re.escape(func_name)}"',    # literal string, double-quoted
                    rf"'{re.escape(func_name)}'",    # literal string, single-quoted
                ]

                for pattern in patterns:
                    if re.search(pattern, py_content):
                        used_functions.add(func_name)
                        break

        except FileNotFoundError:
            print(f"Error: Unable to find python file {py_file_path}", file=sys.stderr)
            return [], []
        except Exception as exception:
            print(f"Error while reading python file: {exception}", file=sys.stderr)
            return [], []

    used = sorted(used_functions)
    unused = sorted(set(function_names) - used_functions)
    return used, unused


def main():
    if len(sys.argv) != 1:
        print("Usage: python check_api_coverage.py")
        sys.exit(1)

    current_dir = Path(__file__).resolve().parent
    src_dir = current_dir.parent / "pysfcgal"
    c_file = src_dir / "sfcgal_def.c"
    py_files = list(src_dir.rglob("*.py"))  # Recursively look for Python files

    print(f"Analysing C file: {c_file}")
    print(f"Checking python files: {py_files}")
    print("-" * 50)

    # Extract functions from the .c file
    c_functions = extract_functions_from_c_file(c_file)

    if not c_functions:
        print("Error: No function found in the C file", file=sys.stderr)
        exit(1)

    print(f"{len(c_functions)} found functions in C file {c_file}")

    # Check usage in the python file
    used, unused = check_function_usage_in_python(py_files, c_functions)

    print(f"\n✅ USED functions ({len(used)}):")
    for used_func in used:
        print(f"  - {used_func}")

    print(f"\n❌ UNUSED functions ({len(unused)}):")
    for unused_func in unused:
        print(f"  - {unused_func}")

    if unused:
        print(f"\n⚠️  {len(unused)} function(s) seem to be unused.")
    else:
        print("\n✅ All the C functions seem to be used.")


if __name__ == "__main__":
    main()
