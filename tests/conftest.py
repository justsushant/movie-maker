import sys
from pathlib import Path

import pytest

# Add project root to sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def real_world_fixture_dir(project_root: Path) -> Path:
    """Directory containing realistic content creator scripts for integration tests."""
    return project_root / "tests" / "fixtures" / "real_world"


@pytest.fixture(scope="session")
def technical_fixture_dir(project_root: Path) -> Path:
    """Directory containing minimal edge case test inputs for technical boundary tests."""
    return project_root / "tests" / "fixtures" / "technical"


@pytest.fixture(scope="session")
def test_output_root(project_root: Path) -> Path:
    return project_root / "output" / "test"


@pytest.fixture(scope="session")
def real_world_output_dir(test_output_root: Path) -> Path:
    """Output directory for real-world scenario integration tests."""
    output_dir = test_output_root / "test_real_world_scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture(scope="session")
def technical_output_dir(test_output_root: Path) -> Path:
    """Output directory for technical boundary integration tests."""
    output_dir = test_output_root / "test_technical_boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
