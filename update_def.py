#!/usr/bin/env python3
"""
Simplified script to clean a SFCGAL C header file for Python CFFI.
"""
import pathlib
import sys

MSVC_IGNORED_FUNCTIONS = [
    "sfcgal_geometry_alpha_shapes",
    "sfcgal_geometry_optimal_alpha_shapes",
]

OUTPUT_UNIX_FILE = pathlib.Path("pysfcgal/sfcgal_def.c")
OUTPUT_WIN_FILE = pathlib.Path("pysfcgal/sfcgal_def_msvc.c")


def check_line_and_add_to_output(cleaned_lines: list[str], line: str) -> None:
    """
    Adds a line to the output if this is not a conditional directive

    Parameters
    ----------
    cleaned_lines : list[str]
        List which contains the generated lines
    line : str
        Line which needs to be added
    """
    # Apply transformations
    line = line.replace("SFCGAL_API ", "")
    ignored_macros = ("#define", "#pragma", "#if", "#elif", "#else", "#endif")
    if not line.strip().startswith(ignored_macros):
        cleaned_lines.append(line)


def try_to_parse_doxygen_block(
    lines: list[str], line_nr: int, windows_version: int
) -> tuple[bool, int]:
    """
    Inspects a Doxygen block to check if the current function is deprecated or needs to
    be skipped.
    If the current line is not the start of a Doxygen block, nothing happens

    Parameters
    ----------
    lines : list[str]
        List which contains the lines of the header input file
    line_nr : int
        Current position of lines.
    windows_version : bool
        In the windows case, functions from MSVC_IGNORED_FUNCTIONS are skipped

    Returns
    -------
    tuple[bool, int]
        True if this is a Doxygen block and the function needs to be added
        The line number where the Doxygen block ends
    """
    # If this not the beginning of a Doxygen block, do nothing
    if "/**" not in lines[line_nr]:
        return (False, line_nr)

    is_deprecated = False
    msvc_skip = False

    # Go through the Doxygen block and the definition
    # Remove the deprecated functions
    # In the windows version, remove the functions
    # not handled by msvc
    deprecations = ["[[deprecated", "[[__deprecated", "SFCGAL_DEPRECATED"]
    while line_nr < len(lines) and ");" not in lines[line_nr]:
        if any(deprecation in lines[line_nr] for deprecation in deprecations):
            is_deprecated = True
        elif windows_version and any(
            func_name in lines[line_nr] for func_name in MSVC_IGNORED_FUNCTIONS
        ):
            msvc_skip = True
        line_nr += 1

    line_nr += 1

    return ((not is_deprecated and not msvc_skip), line_nr)


def clean_header(
    input_file: pathlib.Path, output_file: pathlib.Path, windows_version: bool = False
) -> None:
    """
    Generates a c file of definitions for PySFCGAL based on SFCGAL C API header file

    Parameters
    ----------
    input_file : pathlib.Path
        SFCGAL C API header file
    output_file : pathlib.Path
        PySFCGAL c file to generate
    window_version : bool
        output file for windows compiler. In that case, some functions may be skipped
    """
    with open(input_file, "r") as f_in:
        lines = f_in.readlines()

    cleaned_lines: list[str] = []
    line_nr = 0
    skip_initial = True

    # Skip initial lines (equivalent to '4,/endif/d')
    while line_nr < len(lines) and skip_initial:
        skip_initial = line_nr < 3 or "#endif" not in lines[line_nr]
        line_nr += 1

    # Process the rest of the file
    while line_nr < len(lines):
        # Stop if we find "__cplusplus"
        if "__cplusplus" in lines[line_nr]:
            break

        # If we find a Doxygen block, check if it contains [[deprecated
        # or if is not handled by mscv
        doxygen_start = line_nr
        doxygen_parsed, line_nr = try_to_parse_doxygen_block(
            lines, line_nr, windows_version
        )
        if doxygen_parsed:
            for j in range(doxygen_start, line_nr):
                check_line_and_add_to_output(cleaned_lines, lines[j])
        else:
            # Normal line
            check_line_and_add_to_output(cleaned_lines, lines[line_nr])
            line_nr += 1

    # Add the free() declaration
    cleaned_lines.append("void\nfree(void*);\n")

    # Write the result
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f_out:
        f_out.writelines(cleaned_lines)

    print(f"{output_file} has been updated!")


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        if not input_file.is_file():
            raise FileNotFoundError
    except (IndexError, FileNotFoundError):
        print(f"Usage: {sys.argv[0]} sfcgal_c.h", file=sys.stderr)
        sys.exit(1)

    clean_header(input_file, OUTPUT_UNIX_FILE)
    clean_header(input_file, OUTPUT_WIN_FILE, True)


if __name__ == "__main__":
    main()
