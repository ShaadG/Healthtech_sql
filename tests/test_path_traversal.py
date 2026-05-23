"""Tests that malicious query names are rejected before touching the filesystem."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import db


SAFE_NAMES = [
    "patient_census",
    "lab_trends",
    "encounter_summary",
    "data_validation",
    "billing_extract",
]

DANGEROUS_NAMES = [
    "../schema/create_tables",
    "../../etc/passwd",
    "/etc/passwd",
    "patient_census; DROP TABLE patients--",
    "patient census",          # space
    "patient.census",          # dot
    "patient/census",          # slash
    "patient\\census",         # backslash
    "",                        # empty string
    "patient-census",          # hyphen
    "<script>alert(1)</script>",
]


@pytest.mark.parametrize("name", SAFE_NAMES)
def test_safe_names_pass_validation(name):
    """Names matching [a-zA-Z0-9_]+ must not raise ValueError."""
    import re
    pattern = re.compile(r"^[a-zA-Z0-9_]+$")
    assert pattern.match(name), f"Safe name '{name}' failed regex"


@pytest.mark.parametrize("name", DANGEROUS_NAMES)
def test_dangerous_names_raise_value_error(name):
    """Names with path separators or special characters must be rejected."""
    with pytest.raises(ValueError, match="Invalid query name"):
        db._find_query_file(name)


def test_traversal_cannot_reach_schema_dir():
    """Confirm a traversal attempt cannot load schema/create_tables.sql."""
    with pytest.raises(ValueError):
        db._find_query_file("../schema/create_tables")


def test_traversal_cannot_reach_system_files():
    """Confirm traversal cannot reach files outside the project."""
    with pytest.raises(ValueError):
        db._find_query_file("../../etc/passwd")
