from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def fixture_text_dir(project_root: Path) -> Path:
    return project_root / "tests" / "fixtures" / "text"


@pytest.fixture(scope="session")
def test_output_root(project_root: Path) -> Path:
    return project_root / "output" / "test"
