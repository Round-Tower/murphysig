"""Shared fixtures for benchmark tests."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def cases_yaml(fixtures_dir: Path) -> Path:
    return fixtures_dir / "cases.yaml"


@pytest.fixture
def review_prompt_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "review_prompt.txt"


@pytest.fixture
def judge_prompt_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "judge_prompt.txt"
