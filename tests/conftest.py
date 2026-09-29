import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

VALID_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "valid"

# Stored under another name so that skill installers searching this repository
# for SKILL.md do not offer the fixture skills to consumers.
STORED_SKILL_DOCUMENT = "SKILL.fixture.md"


@pytest.fixture
def conforming_repo(tmp_path):
    """A writable copy of the conforming fixture repository.

    Each violation test mutates exactly one thing in this copy, so the mutation
    in the test body is the whole difference between passing and failing.
    """
    destination = tmp_path / "repo"
    shutil.copytree(VALID_FIXTURE, destination)
    for stored in destination.rglob(STORED_SKILL_DOCUMENT):
        stored.rename(stored.with_name("SKILL.md"))
    return destination
