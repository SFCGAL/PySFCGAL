"""Automatically create Gitlab issues with `glab` command and Gitlab API.

The script creates new issues when there are some unused functions in the C API.

Use it as simply as:

    python scripts/create_gitlab_issues.py

Running the script requires a valid authentification to the PySFCGAL Gitlab project at
https://gitlab.com/sfcgal/pysfcgal.

"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from scripts.check_api_coverage import (check_function_usage_in_python,
                                        extract_functions_from_c_file)


def create_gitlab_issue(title: str, description: str) -> None:
    """Create a Gitlab issue for each function in the provided list

    Args:
        title(str): Title of the Gitlab issue.
        description(str): Description of the Gitlab issue.
    """
    glab_command_components = ["glab", "issue", "create"]
    issue_creation_command = glab_command_components + [
        "--label",
        "Feature",
        "--title",
        title,
        "--description",
        description
    ]
    print(" ".join(issue_creation_command))
    subprocess.run(issue_creation_command)


def generate_gitlab_issues(c_functions: list) -> None:
    """Generate a bunch of new Gitlab issues depending on input functions.

    The SFCGAL function are expected to begin with "sfcgal_", and are sorted with
    respect to the second component of the function name.

    The "sfcgal_geometry_" functions are kept as it is, and a specific Gitlab issue
    is generated for them. The other ones are aggregated so as a single Gitlab issue
    covers all the functions that share the same second component.

    Args:
        c_functions(list): functions for which issues must be created

    """
    sfcgal_issues = defaultdict(list)
    for function in c_functions:
        fname_part = function.split("_")
        if fname_part[0] != "sfcgal" or len(fname_part) == 0:
            print(
                f"Ignoring {function} as its name is invalid (it does not start with "
                "\"sfcgal_\" or does not contains any underscore)."
            )
            continue
        if fname_part[1] == "geometry":
            create_gitlab_issue(
                f"Use {function} in the Python API",
                f"{function} is supported in the C API, but not used in the Python API."
            )
            continue
        sfcgal_issues[fname_part[1]].append(function)
    for function_key, functions in sfcgal_issues.items():
        title = f"Use new C functions related to {function_key}"
        description = (
            "There are a bunch of functions which are supported in the C api, "
            "but still unused in the Python API:\n"
        )
        for func in functions:
            description += f"- {func}\n"
        print(f"{title=}, {description=}")
        create_gitlab_issue(title, description)


def main() -> None:
    if len(sys.argv) != 1:
        print("Usage: python create_gitlab_issues.py")
        sys.exit(1)

    current_dir = Path(__file__).resolve().parent
    src_dir = current_dir.parent / "pysfcgal"
    c_file = src_dir / "sfcgal_def.c"
    py_file = src_dir / "sfcgal.py"

    # Extract functions from the .c file
    c_functions = extract_functions_from_c_file(c_file)

    if not c_functions:
        print("Error: No function found in the C file", file=sys.stderr)
        exit(1)

    print(f"{len(c_functions)} found functions in C file {c_file}")

    # Check usage in the python file
    _, unused = check_function_usage_in_python(py_file, c_functions)

    print(f"\n❌ UNUSED functions ({len(unused)}):")

    generate_gitlab_issues(unused)


if __name__ == "__main__":
    main()
