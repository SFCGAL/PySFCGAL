#!/usr/bin/env python3

import re
import sys
from datetime import datetime


def increment_version(version_date: str) -> None:
    """
    Add YYYYMMDDHHMM suffix to the current dev version
    The script is expected to fail if the current version number
    does not end with .dev suffix.
    This allows to upload a 'latest' package to gitlab package registry.
    Indeed, it is not possible to override an existing package with
    the same version number
    """
    SETUP_FILE = "setup.py"

    try:
        commit_date = datetime.fromisoformat(version_date)
    except ValueError:
        print(f"Error: invalid date ${version_date}")
        sys.exit(1)

    try:
        with open(SETUP_FILE, "r", encoding="utf-8") as f:
            setup_content = f.read()
    except FileNotFoundError:
        print(f"Error: {SETUP_FILE} not found.")
        sys.exit(1)

    # Extract current version number
    # This is supposed to be X.Y.Z.dev
    match = re.search(r'version\s*=\s*"([^"]+)"', setup_content)
    if not match:
        print(f"Error: Unable to find version number in {SETUP_FILE}")
        sys.exit(1)

    current_version = match.group(1)
    print(f"Found version: {current_version}")

    # Check that version ends with ".dev"
    if not current_version.endswith(".dev"):
        print("Error: Version number does not end with '.dev'")
        sys.exit(1)

    # Add date and time to the version number (YYYYMMDDHHMM)
    commit_date_str = commit_date.strftime("%Y%m%d%H%M")
    new_version = current_version + commit_date_str
    print(f"New version: {new_version}")

    new_setup_content = re.sub(
        r'version\s*=\s*"([^"]+)"',
        f'version=\"{new_version}\"',
        setup_content,
        count=1
    )

    # Save the new file
    with open(SETUP_FILE, "w", encoding="utf-8") as f:
        f.write(new_setup_content)

    print(f"{SETUP_FILE} updated successfully.")


if __name__ == "__main__":
    try:
        version_date = sys.argv[1]
    except IndexError:
        print(
            "Usage: ./increment_version.py date_str\n"
            "date_str needs to be in a valid ISO 8601 format"
        )
        sys.exit(1)

    increment_version(version_date)
