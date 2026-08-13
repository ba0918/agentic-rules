import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

VALID_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "valid"


@pytest.fixture
def conforming_repo(tmp_path):
    """A writable copy of the conforming fixture repository.

    Each violation test mutates exactly one thing in this copy, so the mutation
    in the test body is the whole difference between passing and failing.
    """
    destination = tmp_path / "repo"
    shutil.copytree(VALID_FIXTURE, destination)
    return destination
