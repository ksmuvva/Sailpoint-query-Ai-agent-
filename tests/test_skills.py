"""Tests for skill file loading and structure."""

import os
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"

EXPECTED_SKILLS = [
    "sailpoint-research.md",
    "code-generation.md",
    "test-case-creation.md",
    "hld-design.md",
    "lld-design.md",
    "troubleshooting.md",
    "iam-advisory.md",
    "technical-design.md",
]


def test_skills_directory_exists():
    """Verify .claude/skills/ directory exists."""
    assert SKILLS_DIR.exists(), f"Skills directory not found at {SKILLS_DIR}"
    assert SKILLS_DIR.is_dir()


@pytest.mark.parametrize("skill_file", EXPECTED_SKILLS)
def test_skill_file_exists(skill_file):
    """Verify each expected skill file exists."""
    path = SKILLS_DIR / skill_file
    assert path.exists(), f"Skill file not found: {path}"


@pytest.mark.parametrize("skill_file", EXPECTED_SKILLS)
def test_skill_file_has_required_sections(skill_file):
    """Verify each skill file has required structure."""
    path = SKILLS_DIR / skill_file
    content = path.read_text()

    # Every skill should have a title (# heading)
    assert content.startswith("#"), f"{skill_file} should start with a markdown heading"

    # Every skill should have description and trigger
    assert "Description:" in content, f"{skill_file} missing Description"
    assert "Trigger:" in content, f"{skill_file} missing Trigger"

    # Every skill should have instructions
    assert "## Instructions" in content, f"{skill_file} missing Instructions section"

    # Every skill should have a response template
    assert "## Response Template" in content or "## Search Strategy" in content, \
        f"{skill_file} missing Response Template or Search Strategy section"


@pytest.mark.parametrize("skill_file", EXPECTED_SKILLS)
def test_skill_file_not_empty(skill_file):
    """Verify skill files have substantial content."""
    path = SKILLS_DIR / skill_file
    content = path.read_text()

    # Each skill should have at least 500 characters of content
    assert len(content) > 500, f"{skill_file} has too little content ({len(content)} chars)"
