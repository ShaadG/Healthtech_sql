"""Tests that sensitive file types are covered by .gitignore.

These tests protect against accidentally committing databases, exports,
or local config files to GitHub.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
GITIGNORE = REPO_ROOT / ".gitignore"


def _gitignore_lines() -> list[str]:
    return GITIGNORE.read_text().splitlines()


def test_gitignore_exists():
    assert GITIGNORE.exists(), ".gitignore file is missing — create it before git init"


def test_gitignore_blocks_sqlite_db():
    content = GITIGNORE.read_text()
    assert "*.db" in content or "healthtech_dr.db" in content, \
        "*.db must be in .gitignore — never commit the live database"


def test_gitignore_blocks_exports_directory():
    content = GITIGNORE.read_text()
    assert "exports/" in content or "exports" in content, \
        "exports/ must be in .gitignore — CSV exports may contain PHI-adjacent data"


def test_gitignore_blocks_venv():
    content = GITIGNORE.read_text()
    assert ".venv/" in content or "venv/" in content, \
        "Virtual environment directory must be in .gitignore"


def test_gitignore_blocks_pycache():
    content = GITIGNORE.read_text()
    assert "__pycache__/" in content, \
        "__pycache__/ must be in .gitignore"


def test_gitignore_blocks_claude_local_settings():
    content = GITIGNORE.read_text()
    assert ".claude/settings.local.json" in content or ".claude/" in content, \
        ".claude/settings.local.json must be in .gitignore — contains local machine paths"


@pytest.mark.skipif(
    not (REPO_ROOT / ".git").exists(),
    reason="git repo not initialized yet — run 'git init' first"
)
def test_git_check_ignore_database():
    """Verify git itself agrees the .db file is ignored."""
    result = subprocess.run(
        ["git", "check-ignore", "-v", "healthtech_dr.db"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, \
        "healthtech_dr.db is NOT ignored by git — check your .gitignore"


@pytest.mark.skipif(
    not (REPO_ROOT / ".git").exists(),
    reason="git repo not initialized yet — run 'git init' first"
)
def test_git_check_ignore_exports():
    """Verify git itself agrees exports/ is ignored."""
    result = subprocess.run(
        ["git", "check-ignore", "-v", "exports/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, \
        "exports/ is NOT ignored by git — check your .gitignore"
