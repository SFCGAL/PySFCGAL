"""Test the Python snippets contained into the PySFCGAL documentation.
"""

from pathlib import Path

import pytest

mktestdocs = pytest.importorskip("mktestdocs")

DOC_DIR = Path(__file__).parent.parent.parent / "docs"


def test_getting_started():
    mktestdocs.check_md_file(DOC_DIR / "docs/getting_started.md", memory=True)
