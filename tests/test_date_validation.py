"""Tests that date inputs are validated before reaching SQL execution."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))
from cli import _validate_date, cli


VALID_DATES = [
    "2024-01-01",
    "2023-12-31",
    "2000-06-15",
    "1990-01-01",
]

INVALID_DATES = [
    "01-01-2024",       # wrong order
    "2024/01/01",       # wrong separator
    "2024-1-1",         # missing zero padding
    "not-a-date",       # plaintext
    "2024-13-01",       # month out of range
    "2024-01-32",       # day out of range
    "'; DROP TABLE patients--",  # SQL injection attempt
    "<script>",         # XSS attempt
    "2024-01-01; rm -rf /",     # command injection attempt
    "",                 # empty string
    "20240101",         # no separators
]


@pytest.mark.parametrize("date_str", VALID_DATES)
def test_valid_dates_pass(date_str):
    assert _validate_date(date_str, "--start") == date_str


def test_none_date_returns_none():
    assert _validate_date(None, "--start") is None


@pytest.mark.parametrize("date_str", INVALID_DATES)
def test_invalid_dates_raise(date_str):
    with pytest.raises(click.BadParameter):
        _validate_date(date_str, "--start")


def test_cli_query_rejects_bad_start_date():
    runner = CliRunner()
    result = runner.invoke(cli, ["query", "patient_census", "--start", "not-a-date"])
    assert result.exit_code != 0


def test_cli_query_rejects_bad_end_date():
    runner = CliRunner()
    result = runner.invoke(cli, ["query", "patient_census", "--end", "01/01/2024"])
    assert result.exit_code != 0


def test_cli_extract_rejects_bad_date():
    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "billing_extract", "--start", "baddate"])
    assert result.exit_code != 0
